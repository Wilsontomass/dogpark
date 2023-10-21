from dogpark.ais.naive_ai import NaiveAI
from dogpark.game.park import Park


class HeuristicAI(NaiveAI):
    """
    The Heuristic AI isn't quite a full minimax, but it builds on the naive AI by calculating the immediate
    final score of any decision it could make, and always choosing the highest one.
    """

    def choose_destination(self, park: Park) -> int:
        """
        Choose the destination that will result in the highest score.
        """

