import importlib.resources

import yaml

with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
    DOGS = yaml.safe_load(f)


def reload_dogs() -> dict[str, dict]:
    with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
        dogs = yaml.safe_load(f)
    return dogs
