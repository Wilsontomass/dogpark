from typing import Optional

from dogpark.game.objective import objective_description


class Player:

    def __init__(self, colour: str, is_human: bool = True, is_physical: bool = False):
        self.is_human = is_human  # TODO: implement AI
        self.ai = None  # TODO: implement AI
        self.is_physical = is_physical
        self.colour = colour
        self.kennel: dict[str, dict] = {}
        self.lead: dict[str, dict] = {}
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

    def do_selection(self):
        if self.is_human:

            # a lot of trust here that human players aren't cheating
            if self.is_physical:
                print(f"Player {self.colour}, which dogs did you select, seperated by commas?")
                dogs = input().replace(" ", "").split(",")
                print("What did you pay?")
                resources = input().replace(" ", "").split(",")
            else:
                print(f"Player {self.colour}, Choose your dogs:")
                print(self.kennel)
                dogs = input().replace(" ", "").split(",")
                print("What did you pay?")
                resources = input().replace(" ", "").split(",")

            for dog in dogs:
                self.lead[dog] = self.kennel.pop(dog)
            for resource in resources:
                self.resources[resource] -= 1
        else:
            # iterate through and just choose dogs we can afford
            dogs = []
            available_resources = self.resources.copy()
            for dog, dog_stats in self.kennel.items():
                cost: list[str] = dog_stats["c"]  # array like ["STICK", "STICK", "BALL"]
                # turn cost into a dict
                cost: dict[str, int] = {r: cost.count(r) for r in set(cost)}
                if all([available_resources[r] >= cost[r] for r in cost]):
                    dogs.append(dog)
                    for r in cost:
                        available_resources[r] -= cost[r]

                # break if 3 dogs chosen
                if len(dogs) == 3:
                    break

            # subtract resources from player and add dog to lead
            for dog in dogs:
                cost: list[str] = self.kennel[dog]["c"]
                # turn cost into a dict
                cost: dict[str, int] = {r: cost.count(r) for r in set(cost)}
                for r in cost:
                    self.resources[r] -= cost[r]
                self.lead[dog] = self.kennel.pop(dog)

        # add walked to each dog on lead
        for dog in self.lead:
            self.lead[dog]["w"] += 1
