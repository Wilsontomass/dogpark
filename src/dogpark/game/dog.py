import importlib.resources
from enum import Enum, auto

import yaml

dogs = dict()

with open(importlib.resources.files("dogpark.game") / "dogs.yaml") as f:
    dogs = yaml.safe_load(f)
