import importlib.resources

import yaml

with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
    DOGS = yaml.safe_load(f)
