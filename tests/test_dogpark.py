from dogpark.game.game import Dogpark
from dogpark.ais.naive_ai import NaiveAI


def test_dogpark_physical(monkeypatch):
    inputs = iter([
        "y",
        "3",
        "red",
        "yellow",
        "green",
        "y",
        "2",
        "3",
        "4",
        "5",
        "W, H, TE, P, TO, G, U",
        "Canaan_Dog, Fox_Terrier, Large_Munsterlander",
        '{"4": ["SKIP"],"6": ["LOOK"],"8": ["TOY"]}',
        "2",
        "3",
        "4",
    ])
    monkeypatch.setattr('builtins.input', lambda _=None: next(inputs))
    d = Dogpark()


def test_dogpark_automatic():
    d = Dogpark(autorun=True, num_players=3, ais=["NaiveAI", "NaiveAI", "NaiveAI"])


def test_many_dogpark_automatic():
    for _ in range(100):
        d = Dogpark(autorun=True, num_players=3, ais=["NaiveAI", "NaiveAI", "NaiveAI"])


def test_many_dogpark_4_player_automatic():
    results = []
    for _ in range(2000):
        d = Dogpark(autorun=True, num_players=4, ais=["NaiveAI", "NaiveAI", "StingyAI", "StingyAI"], prints=False)
        scores = {player.__class__.__name__: player.final_score(print_breakdown=False) for player in d.state.players}
        results.append(scores)

    print("Average scores:")
    class_scores = {}
    class_games = {}
    for result in results:
        for player, score in result.items():
            class_scores[player] = class_scores.get(player, 0) + score
            class_games[player] = class_games.get(player, 0) + 1

    for player, score in class_scores.items():
        print(f"{player}: {score / class_games[player]}")

