from abc import ABC

from dogpark.game.player import Player


class DogparkAI(Player, ABC):
    """Base class for all AI implementations."""
