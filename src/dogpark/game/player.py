from __future__ import annotations

from abc import abstractmethod, ABC
from typing import Optional

from dogpark.game.park import Park
from dogpark.game.game import Dogpark


class Player(ABC):
    """A base class player of dogpark"""

    def __init__(
            self, game: Dogpark, colour: str, is_physical: bool = False
    ):
        self.game = game
        self.is_physical = is_physical  # governs certain print and input behaviour
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
        self.objective: Optional[int] = None  # may be unknown for physical players

    def __repr__(self):
        return f"{self.colour} - {self.reputation} REP - {self.kennel} - {self.resources} - {self.objective}"

    @abstractmethod
    def choose_objective(self, hard: int = None, easy: int = None) -> Optional[int]:
        """
        Give the player an easy and hard objective, and they choose one. For human players, we may not get a
        response, so we return None in that case.
        """

    @abstractmethod
    def bid(self, available_dogs: dict[str, dict], bids: dict[str, list[tuple[Player, Optional[int]]]]) -> (str, int):
        """for a given dict of dogs, choose one and return its name and bid amount"""

    @abstractmethod
    def choose_dog(self, available_dogs: dict[str, dict]) -> str:
        """for a given dict of dogs, choose one and return its name, for a cost of 1 rep"""

    @abstractmethod
    def do_selection(self) -> list[str]:
        """Select dogs to put on the lead"""

    @abstractmethod
    def apply_bonuses(self, bonuses):
        pass

    @abstractmethod
    def choose_leaving_bonus(self, park: Park) -> list[str]:
        """
        Called when either the player chooses to leave the park, or they are forced to leave the park.
        """

    def apply_bonus(self, bonus: str):
        if bonus in ["STICK", "BALL", "TOY", "TREAT"]:
            self.resources[bonus] += 1
        elif bonus == "REP":
            self.reputation += 1
        elif bonus == "LOOK":
            self.game.look(self)
        elif bonus == "SWAP":
            self.swap(walked=False)
        elif bonus == "WALKED SWAP":
            self.swap(walked=True)

    @abstractmethod
    def swap(self, walked: bool) -> Optional[tuple[str, str]]:
        """
        The player must swap one dog from their kennel with a dog in the field (self.game.dogs). Unless stated
        otherwise (walked=True), all the Walked tokens on the dog leaving the players Kennel are discarded. The player does not place
        the Walked tokens on the new Dog in their Kennel. Swap is always an optional action.

        If walked=True, then the player places a Walked token on the new dog in their Kennel. This Walked token can
        only be placed on the newly acquired Dog.
        """

    @abstractmethod
    def choose_destination(self, park: Park) -> int:
        """Choose a destination to walk to"""

    @abstractmethod
    def pay_walking_bonus(self, park: Park, destination: int) -> bool:
        """Return true if the player would pay the walking bonus for a given destination"""

    def walk(self, park: Park) -> tuple[int, Optional[list[str]]]:
        """
        The player walks in the chosen park. Returns the players destination, and any bonus they took there.
        """
        destination = self.choose_destination(park)

        if destination == 15:
            # choose a leaving bonus
            bonuses = self.choose_leaving_bonus(park)
            return 15, bonuses

        # Move the player to the destination, and apply any bonuses if there are no other players, or they have a
        # social_butterfly dog on their lead. Elsewise, they can choose to pay 1 reputation to get the bonus
        get_bonus = True
        if (
            destination in park.player_positions.values()
            and not any("social_butterfly" == dog["a"] for dog in self.lead.values())
            and self.reputation > 0
        ):
            get_bonus = self.pay_walking_bonus(park, destination)
            if get_bonus:
                self.reputation -= 1

        park.player_positions[self.colour] = destination

        bonuses = None
        if get_bonus:
            bonuses = park.board[destination]
            self.apply_bonuses(bonuses)

        return destination, bonuses

    @abstractmethod
    def look(self, top_cards: dict[str, list[str]]) -> Optional[tuple[str, str]]:
        """
        The player must look at the top 2 cards of the dog deck. This action is performed publicly. The player then
        may choose to replace a dog in the field with 1 of the dog cards they have drawn. The other dog cards are
        discarded.
        """

    def home_time(self):
        """
        Players gain Reputation for the dogs they have on their Lead. Each player performs the following steps:

        1. Gain 2 Reputation for each Dog on their Lead.
        2. Lose 1 Reputation for each Dog without a walked token in their kennel.
        3. Return the Dogs on their Lead to their Kennel.
        """

        # by definition, all dogs on the lead have been walked
        self.reputation += len(self.lead) * 2

        # lose 1 rep for each dog without a walked token
        self.reputation -= sum([1 for dog in self.kennel if self.kennel[dog]["w"] == 0])

        # return dogs to kennel
        self.kennel.update(self.lead)
        self.lead = {}

    def final_score(self) -> int:
        """
        Calculate the final score for this player.

        used at the end of the game, but can also be used to calculate the score at any point in the game,
        as if the game ended at that point.
        """

        rep = self.reputation

        # Player assigns resources to dogs. There isn't actually any optimization to be done here so we can just
        # calculate it.
        for dog in self.kennel.values():
            ability = dog["a"]
            if ability == "pack_dog":
                rep += [d["b"] == dog["b"] for d in self.kennel.values()].count(True) * 2
            elif ability == "raring_to_go":
                rep += dog["w"] * 2
            elif ability == "sociable":
                rep += len(set([d["b"] for d in self.kennel.values()]))
            elif ability in ("stick_chaser", "ball_hog", "toy_collector", "treat_lover"):
                resource = ability.split("_")[0].upper()
                modifier = 2 if resource in ("TREAT", "TOY") else 1
                # add up to 6 of each
                assigned = min(6, self.resources[resource])
                self.resources[resource] -= assigned
                rep += assigned * modifier

        # breed experts
        rep += self.game.calculate_breed_experts()[self.colour][1]

        # objectives
        if self.objective is not None:  # if unknown, assume 0
            # TODO: at the end of the game, we actually do need this
            rep += objective_score(self, self.objective, self.game.num_players)

        # 1 rep for each 5 remaining resources
        rep += sum(self.resources.values()) // 5

        return rep


def objective_score(player: Player, objective: int, num_players: int) -> int:
    """Returns a score based on if a player has completed a certain objective, can be 0, 3 or 7 REP"""
    if objective in (1, 7, 8):
        # assume 4 player game
        breeds = {}
        for dog in player.kennel.values():
            breed = dog["b"]
            breeds[breed] = breeds.get(breed, 0) + 1
            if objective == 1 and breeds[breed] == 4:
                return 7
            elif objective == 7 and breeds[breed] == 3:
                return 3
            elif objective == 8 and len(breeds) == 4:
                return 3
    elif objective in (2, 6):
        dogs_with_2_walked = 0
        for dog in player.kennel.values():
            if dog["w"] >= 2:
                dogs_with_2_walked += 1
                if objective == 2 and dogs_with_2_walked == 3:
                    return 7
                elif objective == 6 and dogs_with_2_walked == 2:
                    return 3
    elif objective == 3:
        walked = sum([dog["w"] for dog in player.kennel.values()])
        if walked >= 10:
            return 7
    elif objective in (4, 9):
        breed_experts_required = 3 if num_players == 4 else 4
        if objective == 9:
            breed_experts_required -= 1
        if player.game.calculate_breed_experts()[player.colour][0] >= breed_experts_required:
            return 7 if objective == 4 else 3
    elif objective in (5, 10):
        dogs_with_1_walked = 0
        for dog in player.kennel.values():
            if dog["w"] >= 1:
                dogs_with_1_walked += 1
                if objective == 5 and dogs_with_1_walked == 7:
                    return 7
                elif objective == 10 and dogs_with_1_walked == 6:
                    return 3

    return 0
