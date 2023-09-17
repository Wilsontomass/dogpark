import random
from typing import Optional

from dogpark.ais.dogpark_ai import DogparkAI
from dogpark.game.park import Park


class NaiveAI(DogparkAI):
    def choose_objective(self, hard: int = None, easy: int = None) -> int:
        return easy

    def bid(self, available_dogs: dict[str, dict], bids: dict[str, list]) -> (str, int):
        # pick a dog that no one else has bid on
        dogs_with_bids = [d for d, b in bids.items() if len(b) > 0]
        dog = random.choice(list(set(available_dogs) - set(dogs_with_bids)))
        return dog, 1

    def choose_dog(self, available_dogs: dict[str, dict]) -> str:
        dog = list(available_dogs.keys())[0]
        return dog

    def do_selection(self) -> list[str]:
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

        return list(self.lead.keys())

    def choose_leaving_bonus(self, park: Park) -> list[str]:
        if len(park.leaving_bonuses) == 0:
            self.reputation -= 1
            return ["-1 REP"]
        # AI always chooses the first leaving bonus
        leaving_bonus = 0
        # apply the leaving bonus
        bonuses = park.leaving_bonuses.pop(leaving_bonus)
        self.apply_bonuses(bonuses)
        return bonuses

    def apply_bonuses(self, bonuses: list[str]):
        # apply the bonus, however player wants to
        bonuses = bonuses.copy()
        while bonuses:
            bonus = random.choice(bonuses)
            bonuses.remove(bonus)
            self.apply_bonus(bonus)

    def choose_destination(self, park: Park) -> int:
        destination = random.choice(park.possible_moves(park.player_positions[self.colour]))
        return destination

    def pay_walking_bonus(self, park: Park, destination: int) -> bool:
        """Return true if the player would pay the walking bonus for a given destination"""
        return True

    def look(self, top_cards: dict[str, list[str]]) -> Optional[tuple[str, str]]:
        field_dog = random.choice(list(self.game.dogs.keys()))
        top_dog = random.choice(list(top_cards.keys()))

        return field_dog, top_dog

    def swap(self, walked: bool) -> Optional[tuple[str, str]]:
        return  # AI doesn't swap for now

