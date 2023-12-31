from dogpark.game.park import Park


def test_park():
    park = Park({}, 3)
    assert set(park.possible_moves(1)) == {2, 3, 4, 5, 10}
    assert set(park.possible_moves(4)) == {5, 10, 6, 11, 7, 12, 8, 13}
    assert set(park.possible_moves(9)) == {15}


def test_skips():
    park = Park({
        4: ["SKIP"],
        6: ["LOOK"],
        8: ["TOY"]
    }, 3)
    assert set(park.possible_moves(1)) == {2, 3, 5, 6, 10, 11}
    assert set(park.possible_moves(3)) == {5, 6, 7, 8, 10, 11, 12, 13}
