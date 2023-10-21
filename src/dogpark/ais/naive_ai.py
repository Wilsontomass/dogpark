import random
from typing import Optional

from dogpark.ais.dogpark_ai import DogparkAI
from dogpark.game.park import Park


class NaiveAI(DogparkAI):
    def choose_objective(self, hard: int = None, easy: int = None) -> int:
        self.objective = easy
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
        # when iterating, shuffle and put unwalked dogs first
        dogs_to_walk = list(self.kennel.items())
        random.shuffle(dogs_to_walk)
        dogs_to_walk = sorted(dogs_to_walk, key=lambda x: x[1]["w"])

        prior_pastoral = False
        if self.game.current_forecast() == 3:
            # put pastoral dogs first
            dogs_to_walk = sorted(dogs_to_walk, key=lambda x: x[1]["b"] == "P", reverse=True)

        for dog, dog_stats in dogs_to_walk:
            cost: list[str] = dog_stats["c"]  # array like ["STICK", "STICK", "BALL"]
            # turn cost into a dict
            cost: dict[str, int] = {r: cost.count(r) for r in set(cost)}
            if all([self.resources[r] >= cost[r] for r in cost]):
                if not prior_pastoral:
                    for r in cost:
                        self.resources[r] -= cost[r]
                if self.game.current_forecast() == 3 and dog_stats["b"] == "P":
                    prior_pastoral = True
                else:
                    prior_pastoral = False

                self.lead[dog] = self.kennel.pop(dog)
            # break if 3 dogs chosen
            if len(self.lead) == (4 if self.game.current_forecast() == 11 else 3):
                break

        # add walked to each dog on lead
        for dog in self.lead:
            self.lead[dog]["w"] += 1

        # AI never uses crafty, but it does use eager
        lead_abilities = self.get_lead_abilities()
        if "eager" in lead_abilities:
            for resource in lead_abilities["eager"]:
                self.resources[resource.upper()] += 1

        if self.game.current_forecast() == 1:
            for dog_dict in (self.lead | self.kennel).values():
                if dog_dict["b"] == "G":
                    self.choose_bonus(self.game.park.location_bonuses)

        return list(self.lead.keys())

    def choose_leaving_bonus(self, park: Park) -> list[str]:
        if len(park.leaving_bonuses) == 0:
            self.reputation -= 1
            return ["-1 REP"]
        # AI always chooses the first (usually best) leaving bonus
        leaving_bonus = 0
        # apply the leaving bonus
        bonuses = park.leaving_bonuses.pop(leaving_bonus)
        self.apply_bonuses(bonuses)
        return bonuses

    def choose_bonus(self, bonuses: list[str]) -> str:
        return random.choice(bonuses)

    def apply_bonuses(self, bonuses: list[str]):
        # apply the bonus, however player wants to
        bonuses = bonuses.copy()
        while bonuses:
            bonus = random.choice(bonuses)
            bonuses.remove(bonus)
            self.apply_bonus(bonus)

    def choose_destination(self, park: Park) -> int:
        possible = park.possible_moves(park.player_positions[self.colour])
        if len(possible) == 1:
            return possible[0]
        without_players = [p for p in possible if p not in park.player_positions.values()]
        if len(without_players) == 1:
            return without_players[0]
        if 15 in without_players:
            without_players.remove(15)
        resources_without_players = {p: park.board[p] for p in without_players}
        # if possible, take resources we are low on
        lowest_resources = []
        smallest = 100
        for resource in self.resources:
            if self.resources[resource] < smallest:
                smallest = self.resources[resource]
                lowest_resources = [resource]
            elif self.resources[resource] == smallest:
                lowest_resources.append(resource)

        for pos, bonuses in resources_without_players.items():
            if any([r in bonuses for r in lowest_resources]):
                return pos

        return random.choice(list(resources_without_players.keys()))

    def pay_walking_bonus(self, park: Park, destination: int) -> bool:
        """Return true if the player would pay the walking bonus for a given destination"""
        return True if self.reputation > 0 else False

    def look(self, top_cards: dict[str, list[str]]) -> Optional[tuple[str, str]]:
        field_dog = random.choice(list(self.game.dogs.keys()))
        top_dog = random.choice(list(top_cards.keys()))

        return field_dog, top_dog

    def swap(self, walked: bool) -> Optional[tuple[str, str]]:
        return  # AI doesn't swap for now


class StingyAI(NaiveAI):
    def pay_walking_bonus(self, park: Park, destination: int) -> bool:
        return False
