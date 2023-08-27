import importlib.resources
import random

import yaml

dogs = dict()

with open(importlib.resources.files("dogpark.game") / "parks.yaml") as f:
    parks = yaml.safe_load(f)


class Park:
    def __init__(self, modifiers: dict):
        """
        Parks contain a map of all locations. each one starts the same, and then we add af ew extra
        resources to each one based on the park card drawn from parks.yaml
        """
        # the keys are the position on the board, where the lower path is 0-9 and the upper is 10-14
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
        for pos, bonus in modifiers.items():
            if bonus == ["SKIP"]:  # if the bonus is skip, we replace the existing bonus
                self.board[pos] = ["SKIP"]
            else:
                self.board[pos].extend(bonus)

    def possible_moves(self, position: int) -> list[int]:
        # given an existing position 1 to 14, return a list of possible positions to move to
        # since a space can be a skipped space, this changes how far away other positions are.
        # a player can always move a distance of 4, but that doesn't count skips.
        # Also, the board isnt just 1-14, but there is an upper and lower path, so position 9
        # goes straight to position 15, and instead position 4 branches off to either position 5 or 10
        # position 15 being "available" means leaving the game board

        def add_targets(targets, pos, dist=5):
            if dist == 0 or pos > 15:
                return
            if pos < len(self.board) and self.board[pos] == ["SKIP"]:
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


def draw_park() -> Park:
    return Park(parks.pop(random.choice(list(parks.keys()))))