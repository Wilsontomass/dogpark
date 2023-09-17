import random
from typing import Optional

from dogpark.game.objective import objective_description
from dogpark.game.park import Park
from dogpark.game.player import Player


class HumanPlayer(Player):

    def choose_objective(self, hard: int = None, easy: int = None):
        """Give the player an easy and hard objective, and they choose one"""
        if self.is_physical:  # in this case, passed easy/hard doesn't matter
            self.objective = None  # we don't know the objective of a physical player
        else:
            print(f"Player {self.colour}, Choose an objective:")
            print(f"Hard: {hard} - {objective_description(hard)}")
            print(f"Easy: {easy} - {objective_description(easy)}")
            self.objective = int(input())

    def bid(self, available_dogs: dict[str, dict], bids: dict[str, list[tuple[Player, Optional[int]]]]) -> (str, int):
        """for a given dict of dogs, choose one and return its name and bid amount"""
        if self.is_physical:
            print(f"Player {self.colour}, which dog did you bid on?")
            dog = input()
            bid = None
        else:
            print(f"Player {self.colour}, Choose a dog:")
            print(available_dogs)
            dog = input()
            bid = int(input("How much would you like to bid? "))
        return dog, bid

    def choose_dog(self, available_dogs: dict[str, dict]) -> str:
        """for a given dict of dogs, choose one and return its name, for a cost of 1 rep"""
        if self.is_physical:
            print(f"Player {self.colour}, which dog did you choose?")
            dog = input()
        else:
            print(f"Player {self.colour}, Choose a dog:")
            print(available_dogs)
            dog = input()
        return dog

    def do_selection(self) -> list[str]:
        # a lot of trust here that human players aren't cheating
        # we dont consider the pastoral dog forecast, since we just ask the player
        # for the cost
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

        # add walked to each dog on lead
        for dog in self.lead:
            self.lead[dog]["w"] += 1

        lead_abilities = self.get_lead_abilities()
        if "eager" in lead_abilities:
            for resource in lead_abilities["eager"]:
                self.resources[resource] += 1

        # crafty?
        if "crafty" in lead_abilities:
            for gain in lead_abilities["crafty"]:
                print(
                    f"You have crafty, and can turn something into {gain.upper()}"
                    f" would you like to use it? (y/n)"
                )
                if input().lower() == "y":
                    print(f"Your resources: {self.resources}")
                    consumed = input("What would you like to consume? ").upper()
                    self.resources[consumed] -= 1
                    self.resources[gain.upper()] += 1

        if self.game.current_forecast() == 1:
            for dog_dict in (self.lead | self.kennel).values():
                if dog_dict["b"] == "G":
                    print(f"You may choose a bonus since you have a Gundog")
                    self.choose_bonus(self.game.park.location_bonuses)

        return dogs

    def choose_leaving_bonus(self, park: Park) -> list[str]:
        """
        Called when either the player chooses to leave the park, or they are forced to leave the park.
        """
        print("Available leaving bonuses:")
        # Print a numbered list of leaving bonuses
        for i, bonus in enumerate(park.leaving_bonuses):
            print(f"{i + 1}: {bonus}")
        if len(park.leaving_bonuses) >= 1:
            print("Choose a leaving bonus:")
            leaving_bonus = int(input()) - 1
        elif len(park.leaving_bonuses) == 0:
            self.reputation -= 1
            return ["-1 REP"]  # no leaving bonuses, so player loses 1 rep
        else:
            leaving_bonus = 0

        # apply the leaving bonus
        bonuses = park.leaving_bonuses.pop(leaving_bonus)
        self.apply_bonuses(bonuses)
        return bonuses

    def choose_bonus(self, bonuses: list[str]) -> str:
        """Choose a single bonus from a list of bonuses"""
        print("Available bonuses:")
        # Print a numbered list of bonuses
        for i, bonus in enumerate(bonuses):
            print(f"  {i + 1}: {bonus}")
        bonus = int(input("Choose bonus: ")) - 1

        # apply the bonus
        self.apply_bonus(bonuses[bonus])
        return bonuses[bonus]

    def apply_bonuses(self, bonuses: list[str]):
        # apply the bonus, however player wants to
        while len(bonuses) > 1:
            bonus = self.choose_bonus(bonuses)
            bonuses.remove(bonus)

        # apply the last bonus
        print("Applying last bonus:", bonuses[0])
        self.apply_bonus(bonuses[0])

    def choose_destination(self, park: Park) -> int:
        """Choose a destination to walk to"""
        return int(input(f"{self.colour}, where would you like to walk to? "))

    def pay_walking_bonus(self, park: Park, destination: int) -> bool:
        """Return true if the player would pay the walking bonus for a given destination"""
        print(f"Player {self.colour}, would you like to pay the walking bonus? (y/n)")
        return input().lower() == "y"

    def look(self, top_cards: dict[str, list[str]]) -> Optional[tuple[str, str]]:
        print("Available dogs in the field:")
        print(self.game.dogs)

        print("Would you like to swap one of these dogs with a dog in the field? (y/n) ")
        will_swap = input().lower() == "y"
        if not will_swap:
            return  # dog cards already discarded because they were popped from the dict
        print("Which field dog would you like to swap?")
        field_dog = input("Dog: ").replace(" ", "_")

        print("Which of the top 2 dogs would you like to swap with?")
        top_dog = input("Dog: ").replace(" ", "_")

        return field_dog, top_dog

    def swap(self, walked: bool) -> Optional[tuple[str, str]]:
        """
        The player must swap one dog from their kennel with a dog in the field (self.game.dogs). Unless stated
        otherwise (walked=True), all the Walked tokens on the dog leaving the players Kennel are discarded. The player does not place
        the Walked tokens on the new Dog in their Kennel. Swap is always an optional action.

        If walked=True, then the player places a Walked token on the new dog in their Kennel. This Walked token can
        only be placed on the newly acquired Dog.
        """
        will_swap = input("Would you like to swap? (y/n) ").lower() == "y"
        if not will_swap:
            return

        print("Your dogs:")
        print(self.kennel)
        print("Which of your dogs would you like to swap?")
        kennel_dog = input("Dog: ").replace(" ", "_")

        print("Available dogs in the field:")
        print(self.game.dogs)
        print("Which available dog would you like to swap with?")
        field_dog = input("Dog: ").replace(" ", "_")
        self.game.swap(self, walked, kennel_dog, field_dog)
