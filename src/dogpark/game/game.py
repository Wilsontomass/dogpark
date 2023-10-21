import random
from typing import Optional

import yaml

from dogpark.game.gamestate import GameState
from dogpark.game.objective import draw_objective_pairs


class Dogpark:
    def __init__(self, autorun: bool = True, num_players: int = None, ais: list[str] = None, prints: bool = True):
        """When created the game is set up"""
        if num_players is None:
            num_players = int(input("How many players? "))
        self.show_hidden = True
        self.ais = ais
        self.prints = prints

        # declare properties before setup
        self.state = GameState(num_players)

        if autorun:
            self.setup()

            for r in range(1, 5):
                self.state.round = r
                self.play_round()

            self.end_game()

    def print(self, *args, **kwargs):
        if self.prints:
            print(*args, **kwargs)

    def setup(self):
        """Set up a game by drawing cards and printing them to the console"""
        from dogpark.game.human import HumanPlayer

        if self.ais is None:
            print("Please enter a list of AI players, seperated by commas:")
            self.ais = input("AIs: ").replace(" ", "").split(",")
        available_colours = ["Red", "Green", "Yellow", "Purple"]
        self.state.players = [get_ai(ai)(self.state, available_colours.pop(), is_physical=False) for ai in self.ais]
        self.state.players += [
            HumanPlayer(self.state, colour, is_physical=False)
            for colour in random.sample(available_colours, self.state.num_players - len(self.state.players))
        ]
        self.state.forecasts = random.sample(range(1, 12), k=4)  # get ids for 4 forecasts
        if self.state.forecasts[0] == 11:  # swap first and second
            self.state.forecasts[0], self.state.forecasts[1] = self.state.forecasts[1], self.state.forecasts[0]
        self.state.breed_experts = [
            "W",
            "H",
            "TE",
            "P",
            "TO",
            "G",
            "U",
        ]
        random.shuffle(self.state.breed_experts)
        self.state.draw_dogs()
        self.state.draw_park()
        if self.prints:
            self.state.print_status()  # players can see the setup before choosing objectives
        available_objectives = draw_objective_pairs(self.state.num_players)
        for player in self.state.players:
            obj = player.choose_objective(*available_objectives.pop())
            if self.show_hidden and obj is not None:
                self.print(f"{player.colour} chose objective {obj}")

    def play_round(self):
        self.print("------------------------------")
        self.play_recruitment()
        self.print("------------------------------")
        self.play_selection()
        self.print("------------------------------")
        self.play_walking()
        self.print("------------------------------")
        self.play_home_time()
        self.print("------------------------------")
        # draw new park
        if self.prints:
            self.state.print_status()

    def play_recruitment(self):
        """Players compete in 2 rounds of Offers to attract their most desired Dogs to their Kennel"""
        self.print("Recruitment")

        for bidding_round in range(1, 3):
            self.print(f"Bidding Round {bidding_round}")
            self.bidding()

            # reset dogs
            self.state.draw_dogs()

    def bidding(self):
        from dogpark.game.player import Player

        players_to_bid = self.state.players.copy()
        # dict of dog name, and then a list of tuples of (player, bid amount). if physical game, bid amount is None
        # until revealed
        bids: dict[str, list[tuple[Player, Optional[int]]]] = {dog_name: [] for dog_name in self.state.dogs}
        for player in players_to_bid:
            dog, amount = player.bid(self.state.dogs, bids)  # Assume players don't read other players bids
            bids[dog].append((player, amount))
            self.print(f"{player.colour} bid on {dog}")

        # resolve bids
        for dog, dog_bids in bids.items():
            if len(dog_bids) > 0:
                # highest bid wins, if tied, first player wins
                winner, amount = max(dog_bids, key=lambda x: x[1])
                winner.reputation -= amount
                winner.add_dog_to_kennel(dog, self.state.dogs.pop(dog))
                players_to_bid.remove(winner)

        # players left without a dog pick from remaining dogs, choosing in turn order
        for player in players_to_bid:
            dog = player.choose_dog(self.state.dogs)
            # TODO: if player has no reputation, then there should be another round of choosing
            player.reputation -= 1
            player.add_dog_to_kennel(dog, self.state.dogs.pop(dog))

    def play_selection(self):
        """Players take turns to place Dogs from their Kennel onto their Lead"""
        self.print("Selection:")
        for player in self.state.players:
            # TODO: maybe AIs could be given an advantage by going last, since the rules state this happens
            #   simultaneously
            selected = player.do_selection()
            if self.state.current_forecast() == 6:
                # 2 rep for each hound
                player.reputation += 2 * [d["b"] for d in player.lead.values()].count("H")
            self.print(f"{player.colour} selected {selected}")

    def play_walking(self):
        """
        Players take turns to walk their Dogs, gaining resources and reputation.
        They keep walking until all but one player has left the park. The last player is then forced to leave.
        """
        self.print("Walking")
        players_walking = self.state.players.copy()
        # all players start at pos -1
        self.state.park.player_positions = {player.colour: -1 for player in players_walking}
        while len(players_walking) > 1:
            for player in players_walking.copy():
                destination, bonuses = player.walk(self.state.park)
                if bonuses is not None:
                    self.print(f"{player.colour} chose bonuses {bonuses}")
                if destination == 15:
                    players_walking.remove(player)
                # if at any point there is only one player left, they are forced to leave (even if they are next to
                # move)
                if len(players_walking) == 1:
                    break

        # last player is forced to leave
        last_player = players_walking.pop()
        bonus_chosen = last_player.choose_leaving_bonus(self.state.park)
        self.print(f"{last_player.colour} chose leaving bonus {bonus_chosen}")

    def play_home_time(self):
        """
        Players gain Reputation for the dogs they have on their Lead. Each player performs the following steps:

        1. Gain 2 Reputation for each Dog on their Lead.
        2. Lose 1 Reputation for each Dog without a walked token in their kennel.
        3. Return the Dogs on their Lead to their Kennel.
        """

        self.print("Home Time")
        for player in self.state.players:
            player.home_time()

        self.state.draw_park()
        self.state.players.append(self.state.players.pop(0))  # rotate players

    def end_game(self):
        self.print("Game over!")
        if self.prints:
            self.state.print_status()
        self.print("Final scores:")
        scores = {
            player: player.final_score(print_breakdown=True if self.prints else False)
            for player in self.state.players
        }
        for player, score in scores.items():
            self.print(f"{player.colour}: {score} REP")

        # check for ties
        max_score = max(scores.values())
        winners = [player for player, score in scores.items() if score == max_score]
        if len(winners) == 1:
            self.print(f"Winner: {winners[0].colour}")
        else:
            # the player who won the highest valued breed expert award (8) wins
            breed_experts = self.state.calculate_breed_experts()
            # if multiple players have the same highest breed expert, then they share the victory
            winners = [colour for colour, score in breed_experts.items() if score[2] == 8]
            if len(winners) == 1:
                self.print(f"Winner: {winners[0]} after winning the 8 point breed expert")
            else:
                self.print(
                    f"Winners: {', '.join([winner for winner in winners])} after jointly winning the"
                    f" 8 point breed expert"
                )

    def save_game(self, name: str):
        """Save to yaml"""
        yml = {
            "round": self.round,
            "num_players": self.num_players,
            "num_dogs": self.num_dogs,
            # TODO: save players
        }
        yaml.dump(yml, open(f"{name}.yml", "w"))


def get_ai(ai_name: str) -> type:
    if ai_name == "NaiveAI":
        from dogpark.ais.naive_ai import NaiveAI

        return NaiveAI

    if ai_name == "StingyAI":
        from dogpark.ais.naive_ai import StingyAI

        return StingyAI


if __name__ == "__main__":
    Dogpark()
