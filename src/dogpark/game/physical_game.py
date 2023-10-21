import json

from dogpark.game.dog import reload_dogs
from dogpark.game.game import Dogpark, get_ai
from dogpark.game.park import Park


class PhysicalDogpark(Dogpark):

    def setup(self):
        """Set up a game by asking the user what cards were drawn in the physical game"""

        print("Please enter Player colours in turn order, starting with the lead player:")
        players = {}
        for i in range(1, self.state.num_players + 1):
            colour = input(f"Player {i} colour: ")
            if input("Is this player an AI? (y/n) ").lower() == "y":
                ai_name = input("AI name: ")
                players[colour] = get_ai(ai_name)(self.state, colour, is_physical=True)
            else:
                from dogpark.game.human import HumanPlayer

                players[colour] = HumanPlayer(self.state, colour, is_physical=True)

        self.state.players = list(players.values())

        if input("Are you playing with Forecast cards? (y/n) ").lower() == "y":
            self.state.forecasts = [int(input(f"Forecast {i}: ")) for i in range(1, 5)]  # or None

        print("please enter the list of breed experts in order, high to low, seperated by commas:")
        self.state.breed_experts = input("Breed Experts: ").replace(" ", "").split(",")

        self.draw_dogs()

        self.draw_park()

        for player in self.state.players:
            obj = player.choose_objective()
            if self.show_hidden and obj is not None:
                print(f"{player.colour} chose objective {obj}")

    def draw_dogs(self):
        print("Please enter the names of the dogs drawn, seperated by commas:")
        dog_names = input("Dogs: ").replace(" ", "").split(",")
        if any([name not in self.state.dogs_deck for name in dog_names]):
            input("Dog name not found, please add it and press enter to continue")
            self.state.dogs_deck = reload_dogs(from_file=True)
            self.draw_dogs()
            return
        self.state.dogs = {name: self.state.dogs_deck.pop(name) for name in dog_names}

    def draw_park(self):
        print("Please enter the dictionary representing the park modifiers drawn:")
        park_str = input("Park: ")
        park_json = json.loads(park_str)
        for key in park_json:  # convert string keys to int keys
            park_json[int(key)] = park_json.pop(key)
        self.state.park = Park(park_json, self.state.num_players)