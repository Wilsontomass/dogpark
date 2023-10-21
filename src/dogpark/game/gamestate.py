import random
from enum import Enum
from typing import Optional

from dogpark.game.dog import reload_dogs
from dogpark.game.forecast import forecast_description
from dogpark.game.park import Park, PARKS


PRINTS = False


class Stage(Enum):
    SETUP = 1
    RECRUITMENT = 2
    SELECTION = 3
    WALKING = 4
    HOME_TIME = 5


class GameState:

    def __init__(self, num_players: int = 3):
        from dogpark.game.player import Player
        self.round = 1
        self.stage = Stage.SETUP
        self.player = None

        self.num_players = num_players
        self.num_dogs = 3 if self.num_players <= 3 else 4

        # general states
        self.players: list[Player] = []
        self.forecasts: list[int] = []
        self.current_forecast = lambda: self.forecasts[self.round - 1]
        self.breed_experts: list[str] = []
        self.park: Optional[Park] = None
        self.dogs_deck = reload_dogs(from_file=False)
        self.parks_deck = PARKS.copy()

        # stage specific states
        #   recruitment
        self.dogs: dict[str, dict] = {}  # always available, but only really matters during bidding
        self.bid_round = 1
        self.bid_state = "bidding"  # "bidding" or "choosing"
        self.players_to_bid: list[Player] = []
        self.bids: dict[str, list[tuple[Player, Optional[int]]]] = {}

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

    def look(self, player, prints: bool = PRINTS):
        """
        The player must look at the top 2 cards of the dog deck. This action is performed publicly. The player then
        may choose to replace a dog in the field with 1 of the dog cards they have drawn. The other dog cards are
        discarded.
        """
        top_cards = {dog: self.dogs_deck.pop(dog) for dog in random.sample(list(self.dogs_deck.keys()), 2)}
        if prints:
            print("Top 2 Dog cards drawn:")
            print(top_cards)

        response = player.look(top_cards)
        if response is None:
            if prints:
                print(f"{player.colour} chose not to swap")
            return
        field_dog, top_dog = response

        del self.dogs[field_dog]
        self.dogs[top_dog] = top_cards[top_dog]
        if prints:
            print(f"Swapped {field_dog} for {top_dog}")

    def draw_dogs(self, prints: bool = PRINTS):
        self.dogs = {k: self.dogs_deck.pop(k) for k in random.sample(list(self.dogs_deck), k=self.num_dogs)}
        if prints:
            print(
                "The following dogs were drawn:",
                ", ".join(self.dogs.keys()),
            )

    def draw_park(self, prints: bool = PRINTS):
        # Draw a park card from parks.yaml
        # Parks numbered 1-8 are for 2-3 players (Rerouted Park)
        # Parks numbered 9-16 are for 4 players (Plentiful Park)
        available_parks = [i for i in range(1, 9)] if self.num_players < 4 else [i for i in range(9, 17)]
        available_parks = list(set(available_parks) & set(self.parks_deck.keys()))
        self.park = Park(self.parks_deck.pop(random.choice(available_parks)), self.num_players)
        if prints:
            print("The following park was drawn:", self.park)

    def swap(self, player, walked: bool, kennel_dog: str, field_dog: str, prints: bool = PRINTS):
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
        if prints:
            print(f"{player.colour} swapped {kennel_dog} for {field_dog}")

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
