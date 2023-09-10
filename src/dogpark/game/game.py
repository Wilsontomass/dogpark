import json
import random

import yaml

from dogpark.game.dog import DOGS
from dogpark.game.forecast import forecast_description
from dogpark.game.objective import draw_objective_pairs
from dogpark.game.park import draw_park, Park
from dogpark.game.player import Player


class Dogpark:

    def __init__(self, autorun: bool = True):
        """When created the game is set up"""
        self.round = 1
        self.is_physical = input("Is this a physical game? (y/n) ").lower() == "y"
        self.num_players = int(input("How many players? "))
        self.num_dogs = 3 if self.num_players <= 3 else 4

        # declare properties before setup
        self.players: list[Player] = []
        self.forecasts: list[int] = []
        self.breed_experts: list[str] = []
        self.dogs_deck: dict[str, dict] = DOGS.copy()  # won't be relevant for physical games
        self.dogs: dict[str, dict] = {}
        self.park: Park = Park({})

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
        player_colour_order = [
            input(f"Player {i} colour: ") for i in range(1, self.num_players + 1)
        ]
        self.players = [Player(colour, is_physical=self.is_physical) for colour in player_colour_order]

        if input("Are you playing with Forecast cards? (y/n) ").lower() == "y":
            self.forecasts = [int(input(f"Forecast {i}: ")) for i in range(1, 5)]  # or None

        print("please enter the list of breed experts in order, high to low, seperated by commas:")
        self.breed_experts = input("Breed Experts: ").replace(" ", "").split(",")

        self.draw_dogs()

        self.draw_park()

        for player in self.players:
            player.choose_objective()

    def setup_console(self):
        """Set up a game by drawing cards and printing them to the console"""
        self.players = [
            Player(colour) for colour in random.sample(["Red", "Green", "Yellow", "Purple"], self.num_players)
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
            player.choose_objective(*available_objectives.pop())

    def draw_dogs(self):
        if self.is_physical:
            print("Please enter the names of the dogs drawn, seperated by commas:")
            dog_names = input("Dogs: ").replace(" ", "").split(",")
            if any([name not in DOGS for name in dog_names]):
                input("Dog name not found, please add it and press enter to continue")
                self.reload_dogs()
                self.draw_dogs()
                return
            self.dogs = {name: DOGS.pop(name) for name in dog_names}
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
            self.park = Park(park_json)
        else:
            self.park = draw_park()
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

    def print_status(self):
        print(f"Round {self.round}")
        print("Players:")
        for i, player in enumerate(self.players):
            prefix = ">>" if i == 0 else "  "
            print(f"{prefix} {player}")
        print("Dogs:")
        print(self.dogs)
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
        players_to_bid = self.players.copy()
        for bidding_round in range(1, 3):
            print(f"Bidding Round {bidding_round}")
            # num_dogs lists of up to num_players bids
            bids: dict[str, list[tuple[Player, int]]] = {dog_name: [] for dog_name in self.dogs}
            for player in players_to_bid:
                dog, amount = player.bid(self.dogs)  # TODO: in physical game, we probably wont receive amount
                bids[dog].append((player, amount))

            # resolve bids
            for dog, dog_bids in bids.items():
                if len(dog_bids) > 0:
                    # highest bid wins, if tied, first player wins
                    winner, amount = max(dog_bids, key=lambda x: x[1])
                    winner.reputation -= amount
                    self.dogs.pop(dog)
                    winner.kennel.append(dog)
                    players_to_bid.remove(winner)

            # players left without a dog pick from remaining dogs, choosing in turn order
            for player in players_to_bid:
                dog = player.choose_dog(self.dogs)
                # TODO: if player has no reputation, then there should be another round of choosing
                player.reputation -= 1
                self.dogs.pop(dog)
                player.kennel.append(dog)
                
            # reset dogs
            self.draw_dogs()

    def play_selection(self):
        """Players take turns to place Dogs from their Kennel onto their Lead"""
        print("Selection")
        for player in self.players:
            # TODO: maybe AIs could be given an advantage by going last, since the rules state this happens
            #   simultaneously
            player.do_selection()

    def play_walking(self):
        pass

    def play_home_time(self):
        pass

    def reload_dogs(self):
        self.dogs_deck = reload_dogs().copy()

    def end_game(self):
        print("Game over!")
        self.print_status()
        print("Final scores:")
        for player in self.players:
            # TODO: Final Scoring
            print(f"{player.colour}: {player.reputation} REP")

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


if __name__ == "__main__":
    Dogpark()
