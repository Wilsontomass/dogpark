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
    d = Dogpark(autorun=True, physical=False, num_players=3, ais=["NaiveAI", "NaiveAI", "NaiveAI"])
