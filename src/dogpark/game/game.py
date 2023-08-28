import json
import random

import yaml

from dogpark.game.dog import draw_dogs, DOGS
from dogpark.game.forecast import forecast_description
from dogpark.game.objective import draw_objective_pairs
from dogpark.game.park import draw_park
from dogpark.game.player import Player


class Dogpark:

    def __init__(self):
        """When created the game is setup"""
        self.round = 1
        self.is_physical = input("Is this a physical game? (y/n) ").lower() == "y"
        self.num_players = int(input("How many players? "))
        self.num_dogs = 3 if self.num_players <= 3 else 4

        # declare properties before setup
        self.players = None
        self.forecasts = None
        self.breed_experts = None
        self.dogs_deck = DOGS.copy()  # won't be relevant for physical games
        self.dogs = None
        self.park = None

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
        self.breed_experts = input("> ").replace(" ", "").split(",")

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
        self.breed_experts = [
            "W",
            "H",
            "TE",
            "P",
            "TO",
            "G",
            "U",
        ]
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
            dog_names = input("> ").replace(" ", "").split(",")
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
            park_str = input("> ")
            self.park = json.loads(park_str)
        else:
            self.park = draw_park()
            print("The following park was drawn:", self.park)

    def play_round(self):
        self.play_recruitment()
        self.play_selection()
        self.play_walking()
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
        print("  \n".join(zip(range(8, 0, -1), self.breed_experts)))

    def play_recruitment(self):
        pass

    def play_selection(self):
        pass

    def play_walking(self):
        pass

    def play_home_time(self):
        pass

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
