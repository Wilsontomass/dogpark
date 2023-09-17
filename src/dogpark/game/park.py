import importlib.resources
import random
from typing import List

import yaml

with open(importlib.resources.files("dogpark.game") / "parks.yaml") as f:
    PARKS = yaml.safe_load(f)


class Park:
    def __init__(self, modifiers: dict, num_players: int):
        """
        Parks contain a map of all locations. each one starts the same, and then we add a few extra
        resources to each one based on the park card drawn from parks.yaml
        """
        # the indices are the positions on the board, where the lower path is 0-9 and the upper is 10-14
        self.board = [
            ["STICK"],
            ["BALL"],
            ["TOY"],
            ["TREAT"],
            ["LOOK"],
            ["BALL"],
            ["SWAP"],
            ["TOY"],
            ["TREAT"],
            ["STICK", "STICK"],
            ["STICK"],
            ["REP"],
            ["LOOK"],
            ["REP"],
            ["BALL", "BALL"],
        ]
        self.is_special = False
        for pos, bonus in modifiers.items():
            if bonus == ["SKIP"]:  # if the bonus is skip, we replace the existing bonus
                self.board[pos] = ["SKIP"]
            else:
                self.board[pos].extend(bonus)

        self.player_positions: dict[str, int] = {}  # colour: position
        self.leaving_bonuses: List[List[str]] = []  # these get consumed when a player leaves the park
        if num_players == 4:
            self.leaving_bonuses.append(["REP", "REP", "REP"])
        self.leaving_bonuses += [
            ["REP", "REP"],
            ["REP", "WALKED SWAP"],
        ]

    def possible_moves(self, position: int) -> list[int]:
        # given an existing position -1 to 14, return a list of possible positions to move to
        # since a space can be a skipped space, this changes how far away other positions are.
        # a player can always move a distance of 4, but that doesn't count skips.
        # Also, the board isnt just 0-14, but there is an upper and lower path, so position 9
        # goes straight to position 15, and instead position 4 branches off to either position 5 or 10
        # position 15 being "available" means leaving the game board

        def add_targets(targets, pos, dist=5):
            if dist == 0 or pos > 15:
                return
            if 0 <= pos < len(self.board) and self.board[pos] == ["SKIP"]:
                dist += 1  # skips add 1 to the distance
            else:
                targets.add(pos)
            if pos == 4:  # branch
                add_targets(targets, 10, dist - 1)
            if pos == 9:  # "branch"
                add_targets(targets, 15, dist - 1)
                return  # don't go to 10
            add_targets(targets, pos + 1, dist - 1)

        possible = set()
        add_targets(possible, position)
        possible.remove(position)  # you can't stay in the same place

        return list(possible)

    def __repr__(self):
        return f"{self.board}"


def draw_park(num_players: int) -> Park:
    """
    Draw a park card from parks.yaml
    Parks numbered 1-8 are for 2-3 players (Rerouted Park)
    Parks numbered 9-16 are for 4 players (Plentiful Park)
    """
    available_parks = [i for i in range(1, 9)] if num_players < 4 else [i for i in range(9, 17)]
    return Park(PARKS.pop(random.choice(available_parks)), num_players)
