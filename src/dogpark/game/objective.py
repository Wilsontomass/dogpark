import random
from typing import List, Tuple

OBJECTIVE_DESCRIPTIONS = {
    1: "If the player has 4 Dogs of the same breed category in their kennel during final scoring, they score 7"
       " REP. Only use for 4 player game.",
    2: "If the player has 3 different Dogs in their Kennel who each have at least 2 WALKED on them during final"
       " scoring, they gain 7 REP.",
    3: "If the player has  at least 10 WALKED across their Kennel during final scoring, they gain 7 REP. It does not"
       " matter how these WALKED are distributed across Dogs.",
    4: "in a 2/3-player game, if the player has won at least 4 Breed Expert awards, they gain 7 REP. In a 4-player"
       " game, if the player has won at least 3 Breed Expert awards, they gain 7 REP. Any awards where the victory"
       " is tied still count towards this Objective.",
    5: "If the player has 7 Dogs who each have at least 1 WALKED on them in their Kennel, they gain 7 REP.",
    6: "If the player has 2 different DOgs in their Kennel who each have at least 2 WALKED on them during final"
       " scoring, they gain 3 REP",
    7: "If the player has 3 Dogs of the same breed category in their Kennel during final scoring, they gain 3 REP.",
    8: "If the player has at least 1 dog of 4 different breed categories in their Kennel during final scoring, they"
       " gain 3 REP.",
    9: "In a 2/3-player game, if the player has won at least 3 Breed Expert awards, they gain 3 REP. In a 4-player"
       " game, if the player has won at least 2 Breed Expert awards, they gain 3 REP. Any awards where the victory"
       " is tied still count towards this Objective.",
    10: "If the player has 6 Dogs who each have at least 1 WALKED on them in their Kennel, they gain 3 REP.",
}


def objective_description(objective_id: int):
    return OBJECTIVE_DESCRIPTIONS[objective_id]

