import json
import random
from typing import Optional

import yaml

from dogpark.game.dog import reload_dogs
from dogpark.game.forecast import forecast_description
from dogpark.game.objective import draw_objective_pairs
from dogpark.game.park import Park, PARKS


class Dogpark:

    def __init__(
            self, autorun: bool = True, physical: bool = None, num_players: int = None, ais: list[str] = None
    ):
        """When created the game is set up"""
        from dogpark.game.player import Player
        self.round = 1
        if physical is None:
            physical = input("Is this a physical game? (y/n) ").lower() == "y"
        if num_players is None:
            num_players = int(input("How many players? "))
        self.is_physical = physical
        self.num_players = num_players
        self.num_dogs = 3 if self.num_players <= 3 else 4
        self.show_hidden = True
        self.ais = ais

        # declare properties before setup
        self.players: list[Player] = []
        self.forecasts: list[int] = []
        self.current_forecast = lambda: self.forecasts[self.round - 1]
        self.breed_experts: list[str] = []
        self.dogs_deck: dict[str, dict] = reload_dogs()  # won't be relevant for physical games
        self.parks_deck: dict[str, dict] = PARKS.copy()  # won't be relevant for physical games
        self.dogs: dict[str, dict] = {}
        self.park: Park = Park({}, self.num_players)

        if autorun:
            if self.is_physical:
                self.setup_physical()
            else:
                self.setup_console()

            for r in range(1, 5):
                self.round = r
                self.play_round()

            self.end_game()

    def setup_physical(self):
        """Set up a game by asking the user what cards were drawn in the physical game"""

        print("Please enter Player colours in turn order, starting with the lead player:")
        players = {}
        for i in range(1, self.num_players + 1):
            colour = input(f"Player {i} colour: ")
            if input("Is this player an AI? (y/n) ").lower() == "y":
                ai_name = input("AI name: ")
                players[colour] = get_ai(ai_name)(self, colour, is_physical=self.is_physical)
            else:
                from dogpark.game.human import HumanPlayer
                players[colour] = HumanPlayer(self, colour, is_physical=self.is_physical)

        self.players = list(players.values())

        if input("Are you playing with Forecast cards? (y/n) ").lower() == "y":
            self.forecasts = [int(input(f"Forecast {i}: ")) for i in range(1, 5)]  # or None

        print("please enter the list of breed experts in order, high to low, seperated by commas:")
        self.breed_experts = input("Breed Experts: ").replace(" ", "").split(",")

        self.draw_dogs()

        self.draw_park()

        for player in self.players:
            obj = player.choose_objective()
            if self.show_hidden and obj is not None:
                print(f"{player.colour} chose objective {obj}")

    def setup_console(self):
        """Set up a game by drawing cards and printing them to the console"""
        from dogpark.game.human import HumanPlayer
        if self.ais is None:
            print("Please enter a list of AI players, seperated by commas:")
            self.ais = input("AIs: ").replace(" ", "").split(",")
        available_colours = ["Red", "Green", "Yellow", "Purple"]
        self.players = [
            get_ai(ai)(self, available_colours.pop(), is_physical=self.is_physical)
            for ai in self.ais
        ]
        self.players += [
            HumanPlayer(self, colour, is_physical=self.is_physical)
            for colour in random.sample(available_colours, self.num_players - len(self.players))
        ]
        self.forecasts = random.sample(range(1, 12), k=4)  # get ids for 4 forecasts
        if self.forecasts[0] == 11:  # swap first and second
            self.forecasts[0], self.forecasts[1] = self.forecasts[1], self.forecasts[0]
        self.breed_experts = ["W", "H", "TE", "P", "TO", "G", "U", ]
        random.shuffle(self.breed_experts)
        self.draw_dogs()
        self.draw_park()
        self.print_status()  # players can see the setup before choosing objectives
        available_objectives = draw_objective_pairs(self.num_players)
        for player in self.players:
            obj = player.choose_objective(*available_objectives.pop())
            if self.show_hidden and obj is not None:
                print(f"{player.colour} chose objective {obj}")

    def draw_dogs(self):
        if self.is_physical:
            print("Please enter the names of the dogs drawn, seperated by commas:")
            dog_names = input("Dogs: ").replace(" ", "").split(",")
            if any([name not in self.dogs_deck for name in dog_names]):
                input("Dog name not found, please add it and press enter to continue")
                self.reload_dogs()
                self.draw_dogs()
                return
            self.dogs = {name: self.dogs_deck.pop(name) for name in dog_names}
        else:
            self.dogs = {k: self.dogs_deck.pop(k) for k in random.sample(list(self.dogs_deck), k=self.num_dogs)}
            print(
                "The following dogs were drawn:",
                ", ".join(self.dogs.keys()),
            )

    def draw_park(self):
        if self.is_physical:
            print("Please enter the dictionary representing the park modifiers drawn:")
            park_str = input("Park: ")
            park_json = json.loads(park_str)
            for key in park_json:  # convert string keys to int keys
                park_json[int(key)] = park_json.pop(key)
            self.park = Park(park_json, self.num_players)
        else:
            # Draw a park card from parks.yaml
            # Parks numbered 1-8 are for 2-3 players (Rerouted Park)
            # Parks numbered 9-16 are for 4 players (Plentiful Park)
            available_parks = [i for i in range(1, 9)] if self.num_players < 4 else [i for i in range(9, 17)]
            available_parks = list(set(available_parks) & set(self.parks_deck.keys()))
            self.park = Park(self.parks_deck.pop(random.choice(available_parks)), self.num_players)
            print("The following park was drawn:", self.park)

    def play_round(self):
        print("------------------------------")
        self.play_recruitment()
        print("------------------------------")
        self.play_selection()
        print("------------------------------")
        self.play_walking()
        print("------------------------------")
        self.play_home_time()
        print("------------------------------")
        # draw new park
        self.draw_park()
        self.print_status()

    def print_status(self):
        print(f"Round {self.round}")
        print("Players:")
        for i, player in enumerate(self.players):
            prefix = ">>" if i == 0 else "  "
            print(f"{prefix} {player}")
        print("Dogs:")
        print(self.dogs)
        print("Dog deck size:", len(self.dogs_deck))
        print("Park:")
        print(self.park)
        print("Forecasts:")
        for i, forecast in enumerate(self.forecasts):
            prefix = ">>" if i + 1 == self.round else "  "
            print(f"{prefix} Round {i + 1}: {forecast_description(forecast)}")
        print("Breed Experts:")
        print("\n".join([f"{8 - i}: {breed}" for i, breed in enumerate(self.breed_experts)]))

    def play_recruitment(self):
        """Players compete in 2 rounds of Offers to attract their most desired Dogs to their Kennel"""
        print("Recruitment")

        for bidding_round in range(1, 3):
            print(f"Bidding Round {bidding_round}")
            if self.is_physical:
                self.physical_bidding()
            else:
                self.automated_bidding()
                
            # reset dogs
            self.draw_dogs()

    def automated_bidding(self):
        from dogpark.game.player import Player
        players_to_bid = self.players.copy()
        # dict of dog name, and then a list of tuples of (player, bid amount). if physical game, bid amount is None
        # until revealed
        bids: dict[str, list[tuple[Player, Optional[int]]]] = {dog_name: [] for dog_name in self.dogs}
        for player in players_to_bid:
            dog, amount = player.bid(self.dogs, bids)  # Assume players don't read other players bids
            bids[dog].append((player, amount))
            print(f"{player.colour} bid on {dog}")

        # resolve bids
        for dog, dog_bids in bids.items():
            if len(dog_bids) > 0:
                # highest bid wins, if tied, first player wins
                winner, amount = max(dog_bids, key=lambda x: x[1])
                winner.reputation -= amount
                winner.add_dog_to_kennel(dog, self.dogs.pop(dog))
                players_to_bid.remove(winner)

        # players left without a dog pick from remaining dogs, choosing in turn order
        for player in players_to_bid:
            dog = player.choose_dog(self.dogs)
            # TODO: if player has no reputation, then there should be another round of choosing
            player.reputation -= 1
            player.add_dog_to_kennel(dog, self.dogs.pop(dog))

    def physical_bidding(self):
        pass  # TODO: implement

    def play_selection(self):
        """Players take turns to place Dogs from their Kennel onto their Lead"""
        print("Selection:")
        for player in self.players:
            # TODO: maybe AIs could be given an advantage by going last, since the rules state this happens
            #   simultaneously
            selected = player.do_selection()
            if self.current_forecast() == 6:
                # 2 rep for each hound
                player.reputation += 2 * [d["b"] for d in player.lead.values()].count("H")
            print(f"{player.colour} selected {selected}")

    def play_walking(self):
        """
        Players take turns to walk their Dogs, gaining resources and reputation.
        They keep walking until all but one player has left the park. The last player is then forced to leave.
        """
        print("Walking")
        players_walking = self.players.copy()
        # all players start at pos -1
        self.park.player_positions = {player.colour: -1 for player in players_walking}
        while len(players_walking) > 1:
            for player in players_walking.copy():
                destination, bonuses = player.walk(self.park)
                if bonuses is not None:
                    print(f"{player.colour} chose bonuses {bonuses}")
                if destination == 15:
                    players_walking.remove(player)
                # if at any point there is only one player left, they are forced to leave (even if they are next to
                # move)
                if len(players_walking) == 1:
                    break

        # last player is forced to leave
        last_player = players_walking.pop()
        bonus_chosen = last_player.choose_leaving_bonus(self.park)
        print(f"{last_player.colour} chose leaving bonus {bonus_chosen}")

    def play_home_time(self):
        """
        Players gain Reputation for the dogs they have on their Lead. Each player performs the following steps:

        1. Gain 2 Reputation for each Dog on their Lead.
        2. Lose 1 Reputation for each Dog without a walked token in their kennel.
        3. Return the Dogs on their Lead to their Kennel.
        """

        print("Home Time")
        for player in self.players:
            player.home_time()

    def reload_dogs(self):
        self.dogs_deck = reload_dogs(from_file=True)

    def end_game(self):
        print("Game over!")
        self.print_status()
        print("Final scores:")
        scores = {player: player.final_score(print_breakdown=True) for player in self.players}
        for player, score in scores.items():
            print(f"{player.colour}: {score} REP")

        # check for ties
        max_score = max(scores.values())
        winners = [player for player, score in scores.items() if score == max_score]
        if len(winners) == 1:
            print(f"Winner: {winners[0].colour}")
        else:
            # the player who won the highest valued breed expert award (8) wins
            breed_experts = self.calculate_breed_experts()
            # if multiple players have the same highest breed expert, then they share the victory
            winners = [colour for colour, score in breed_experts.items() if score[2] == 8]
            if len(winners) == 1:
                print(f"Winner: {winners[0]} after winning the 8 point breed expert")
            else:
                print(f"Winners: {', '.join([winner for winner in winners])} after jointly winning the"
                      f" 8 point breed expert")

    def save_game(self, name: str):
        """Save to yaml"""
        yml = {
            "round": self.round,
            "is_physical": self.is_physical,
            "num_players": self.num_players,
            "num_dogs": self.num_dogs,
            # TODO: save players
        }
        yaml.dump(yml, open(f"{name}.yml", "w"))

    def calculate_breed_experts(self) -> dict[str, tuple[int, int, int]]:
        """return a dict of player colour and a tuple of: number of awards, points from awards, and highest award"""
        breed_experts = {p.colour: [0, 0, 0] for p in self.players}
        for i, breed in enumerate(self.breed_experts):
            # players get score if they have the most of a certain breed in their kennel. If there is a tie, all tied
            # players get the points
            value = 8 - i
            dogs = {p.colour: len([d for d in p.kennel.values() if d["b"] == breed]) for p in self.players}
            maxdogs = max(dogs.values())
            for winner_colour in [c for c, v in dogs.items() if v == maxdogs]:
                breed_experts[winner_colour][0] += 1
                breed_experts[winner_colour][1] += value
                breed_experts[winner_colour][2] = max(breed_experts[winner_colour][2], value)
        return breed_experts

    def look(self, player):
        """
        The player must look at the top 2 cards of the dog deck. This action is performed publicly. The player then
        may choose to replace a dog in the field with 1 of the dog cards they have drawn. The other dog cards are
        discarded.
        """
        top_cards = {dog: self.dogs_deck.pop(dog) for dog in random.sample(list(self.dogs_deck.keys()), 2)}
        print("Top 2 Dog cards drawn:")
        print(top_cards)

        response = player.look(top_cards)
        if response is None:
            print(f"{player.colour} chose not to swap")
            return
        field_dog, top_dog = response

        del self.dogs[field_dog]
        self.dogs[top_dog] = top_cards[top_dog]
        print(f"Swapped {field_dog} for {top_dog}")

    def swap(self, player, walked: bool, kennel_dog: str, field_dog: str):
        kennel_dict = player.kennel.pop(kennel_dog)
        field_dict = self.dogs.pop(field_dog)
        if "w" in kennel_dict:
            del kennel_dict["w"]

        if walked:
            field_dict["w"] = 1

        if self.current_forecast() == 10:
            field_dict["w"] = 1  # could end up with 2 walked this way

        player.add_dog_to_kennel(field_dog, field_dict)
        self.dogs[kennel_dog] = kennel_dict
        print(f"{player.colour} swapped {kennel_dog} for {field_dog}")


def get_ai(ai_name: str) -> type:
    if ai_name == "NaiveAI":
        from dogpark.ais.naive_ai import NaiveAI
        return NaiveAI


if __name__ == "__main__":
    Dogpark()
