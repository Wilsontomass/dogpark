import copy
import importlib.resources

import yaml


def reload_dogs(from_file: bool = False) -> dict[str, dict]:
    if from_file:
        with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
            dogs = yaml.safe_load(f)
    else:
        return copy.deepcopy(DOGS)

    # init walked at 0 for all dogs
    for dog in dogs:
        dogs[dog]["w"] = 0
    return dogs


DOGS = reload_dogs(True)
