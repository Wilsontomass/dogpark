import random

from dogpark.game import dog


def dogpark():
    """Run dogpark"""
    round = 1
    dogs = draw_dogs()


def draw_dogs() -> list[dict]:
    return random.sample(dog.dogs, 3)
