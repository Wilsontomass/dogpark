

class Player:

    def __init__(self, colour: str):
        self.kennel = []
        self.lead = []
        self.reputation = 5

    def __repr__(self):
        return f"{self.reputation}, {self.kennel}, {self.lead}"
