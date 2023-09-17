import importlib.resources

import yaml


def reload_dogs() -> dict[str, dict]:
    with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
        dogs = yaml.safe_load(f)
        # init walked at 0 for all dogs
    for dog in dogs:
        dogs[dog]["w"] = 0
    return dogs


DOGS = reload_dogs()
