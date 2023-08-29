from typing import Optional

from dogpark.game.objective import objective_description


class Player:

    def __init__(self, colour: str, is_human: bool = True, is_physical: bool = False):
        self.is_human = is_human  # TODO: implement AI
        self.ai = None  # TODO: implement AI
        self.is_physical = is_physical
        self.colour = colour
        self.kennel = []
        self.lead = []
        self.reputation = 5
        self.resources = {
            "STICK": 2,
            "BALL": 2,
            "TOY": 1,
            "TREAT": 1,
        }
        self.objective: Optional[int] = None

    def choose_objective(self, hard: int = None, easy: int = None):
        """Give the player an easy and hard objective, and they choose one"""
        if self.is_human:
            if self.is_physical:  # in this case, passed easy/hard doesn't matter
                print(f"Player {self.colour}, which objective number did you choose?")
                # TODO: consider that this may be hidden from the program if playing against physical players
                self.objective = int(input())
            else:
                print(f"Player {self.colour}, Choose an objective:")
                print(f"Hard: {hard} - {objective_description(hard)}")
                print(f"Easy: {easy} - {objective_description(easy)}")
                self.objective = int(input())
        else:
            self.objective = easy  # TODO: implement AI
            if self.is_physical:
                print(f"{self.colour} chose {self.objective}")

    def bid(self, available_dogs: dict[str, dict]) -> (str, int):
        """for a given dict of dogs, choose one and return its name and bid amount"""
        if self.is_human:
            if self.is_physical:
                print(f"Player {self.colour}, which dog did you bid on?")
                dog = input()
                # TODO: consider that this may be hidden from the program if playing against physical players
                bid = int(input("How much did you bid? "))
            else:
                print(f"Player {self.colour}, Choose a dog:")
                print(available_dogs)
                dog = input()
                bid = int(input("How much would you like to bid? "))
            return dog, bid

        else:
            dog = list(available_dogs.keys())[0]  # TODO: implement AI
            print(f"{self.colour} chose {dog}")
            return dog, 1

    def choose_dog(self, available_dogs: dict[str, dict]) -> str:
        """for a given dict of dogs, choose one and return its name, for a cost of 1 rep"""
        if self.is_human:
            if self.is_physical:
                print(f"Player {self.colour}, which dog did you choose?")
                dog = input()
            else:
                print(f"Player {self.colour}, Choose a dog:")
                print(available_dogs)
                dog = input()
        else:
            dog = list(available_dogs.keys())[0]  # TODO: implement AI
            print(f"{self.colour} chose {dog}")
        return dog

    def __repr__(self):
        return f"{self.colour} - {self.reputation} REP - {self.kennel} - {self.resources} - {self.objective}"
