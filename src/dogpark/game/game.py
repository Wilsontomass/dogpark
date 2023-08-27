import random

from dogpark.game import dog
from dogpark.game.player import Player


def dogpark(num_players: int = 3) -> None:
    """Run dogpark"""
    round = 1  # start at round 1
    forecast_ids = random.sample(range(1, 12), k=4)  # get ids for 4 forecasts
    num_drawn_dogs = 3 if num_players <= 3 else 4  # get 3 or 4 dogs
    dogs = draw_dogs(num_drawn_dogs)
    players = [Player(colour) for colour in random.sample(["Red", "Green", "Yellow", "Purple"], num_players)]  # create players
    breed_experts = [
        "W",
        "H",
        "TE",
        "P",
        "TO",
        "G",
        "U",
    ]
    random.shuffle(breed_experts)
    location = draw_location()
    print(forecast_ids, breed_experts, players)


def draw_dogs(num_dogs) -> list[dict]:
    # Return a list of 3 dog dictionaries, removed from the dog.dogs dictionary
    return [dog.dogs.pop(random.choice(list(dog.dogs.keys()))) for _ in range(num_dogs)]
