FORECAST_DESCRIPTIONS = {
    1: "During SELECTION, for each GUNDOG that the player places on their Lead or that is in their Kennel,"
    " the player can gain 1 Location Bonus. The player can choose from any Location Bonus currently in the Park."
    " If a player has multiple GUNDOGS they are able to choose multiple of the same Location Bonus."
    " Players cannot choose SWAP or LOOK Location Bonuses.",
    2: "During HOME TIME, players gain 2 ANY for each TERRIER in their Kennel or on their Lead.",
    3: "During SELECTION, if a player places a PASTORAL Dog on their Lead, then the next Dog placed onto their Lead"
    " may be placed without paying its walking cost. Players must have capacity on their Lead.",
    4: "During HOME TIME, players gain 1 REP and 1 ANY for each WORKING Dog in their Kennel or on their Lead.",
    5: "During HOME TIME, players gain 3 REP for each TOY Dog in their Kennel or on their Lead.",
    6: "During SELECTION, for each HOUND that the player places on their Lead, they gain 2 REP",
    7: "During the entire round, if the player place a UTILITY Dog onto their Kennel, either in Recruitment or"
    " through SWAP, they gain 1 REP and 1 ANY. This gain is immediate, and the Dog does not have to be in the"
    " player's Kennel at the end of the round.",
    8: "During HOME TIME, players lose 2 REP per dog instead of 1 REP for Dogs without WALKED.",
    9: "During HOME TIME, players lose 0 REP per dog instead of 1 REP for Dogs without WALKED.",
    10: "During the entire round, whenever the player SWAPs they place WALKED on the newly acquired Dog in their"
    " Kennel. The Leaving Bonus SWAP is included - this would see the player gain 2 WALKED for the newly acquired"
    " DOG",
    11: "During the entire round, Players may place 4 Dogs on their Lead during SELECTION, if they have the resources"
    " to do so. The 4th Dog is placed to the right of the Lead. This card cannot be placed on the 1st Forecast"
    " space. If it is drawn first, place it into the 2nd position and place the next forecast card in the"
    " 1st position.",
}


def forecast_description(forecast_id: int):
    return FORECAST_DESCRIPTIONS[forecast_id]


def _1():
    # During SELECTION, gain 1 Location Bonus for each GUNDOG in your Kennel or on your Lead. (Excludes SWAP and LOOK)
    pass
