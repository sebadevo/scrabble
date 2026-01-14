from collections import Counter

import pytest

from scrabble.main import (
    ask_word,
    draw_hand,
    get_direction,
    get_position,
    get_word,
    initialise_board,
    initialise_tile_bag,
    load_occurrences_and_points,
    verify_board_boundaries,
    verify_first_word_centered,
)


def test_load_fichier_lettres() -> None:
    """Tests `load_occurrences_and_points`.

    This test uses the known expected distributions for each Scrabble letter (A-Z) and asserts that the function returns
    two dictionaries: one mapping each letter to its occurrence count and another mapping each letter to its point
    value.
    """
    file_name = "resources/Lettres.txt"
    expected_occurrence = {
        "A": 9,
        "B": 2,
        "C": 2,
        "D": 3,
        "E": 15,
        "F": 2,
        "G": 2,
        "H": 2,
        "I": 8,
        "J": 1,
        "K": 1,
        "L": 5,
        "M": 3,
        "N": 6,
        "O": 6,
        "P": 2,
        "Q": 1,
        "R": 6,
        "S": 6,
        "T": 6,
        "U": 6,
        "V": 2,
        "W": 1,
        "X": 1,
        "Y": 1,
        "Z": 1,
    }
    expected_points = {
        "A": 1,
        "B": 3,
        "C": 3,
        "D": 2,
        "E": 1,
        "F": 4,
        "G": 2,
        "H": 4,
        "I": 1,
        "J": 8,
        "K": 10,
        "L": 1,
        "M": 2,
        "N": 1,
        "O": 1,
        "P": 3,
        "Q": 8,
        "R": 1,
        "S": 1,
        "T": 1,
        "U": 1,
        "V": 4,
        "W": 10,
        "X": 10,
        "Y": 10,
        "Z": 10,
    }

    occurrence, points = load_occurrences_and_points(file_name)

    assert expected_occurrence == occurrence
    assert expected_points == points


def test_pioche_init() -> None:
    """Test that initialise_tile_bag builds the expected initial tile bag.

    Given a mapping of letter occurrences, verifies that the function returns a
    string containing each letter repeated the correct number of times, in the
    expected order.
    """
    occurrence_lettres = {"E": 5, "A": 7}
    output = initialise_tile_bag(occurrence_lettres)
    expected_output = "AAAAAAAEEEEE"
    assert output == expected_output


def test_plateau_init() -> None:
    """Test that initialise_board creates a board with the requested dimensions filled with underscores."""
    lines, columns = 3, 4
    plateau = initialise_board((lines, columns))
    expected_plateau = [
        ["_", "_", "_", "_"],
        ["_", "_", "_", "_"],
        ["_", "_", "_", "_"],
    ]
    assert expected_plateau == plateau


def test_get_position(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_position() keeps prompting until a valid board position is entered.

    Simulates successive user inputs via monkeypatch, providing invalid values
    (non-numeric and out-of-range) before a valid value ("5"), and asserts the
    function returns the expected integer position.
    """
    position = "5"
    all_inputs = ["dummy_Value", "-5", "30", position]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert int(position) == get_position("dummy_value")


def test_get_direction(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that `get_direction()` repeatedly prompts until it receives a valid input."""
    direction = "V"
    all_inputs = ["Dummy_value", 5, "v"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert direction == get_direction()

    direction = "H"
    all_inputs = ["Dummy_value", 5, "h"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert direction == get_direction()

    direction = "V"
    all_inputs = ["Dummy_value", 5, "V"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert direction == get_direction()

    direction = "H"
    all_inputs = ["Dummy_value", 5, "H"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert direction == get_direction()


def test_get_mot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that get_word() repeatedly prompts until it receives a valid word input."""
    mot = "hello"
    all_inputs = ["123", "hey1", mot]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert mot.upper() == get_word()


def test_propose_mot(monkeypatch: pytest.MonkeyPatch) -> None:
    """Test that ask_word() correctly collects word placement inputs from the user."""
    all_inputs = ["5", "5", "H", "hello"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    expected_output = ("HELLO", (5, 5), "H")
    assert expected_output == ask_word()


def test_verif_bornes_passes_horizontally() -> None:
    """Test that verify_board_boundaries returns True for a valid horizontal word placement."""
    coup = ("BONJOUR", (7, 7), "H")
    dimension = (15, 15)
    assert verify_board_boundaries(coup, dimension) is True


def test_verif_bornes_passes_vertically() -> None:
    """Test that verify_board_boundaries returns True for a valid vertical word placement."""
    coup = ("BONJOUR", (7, 7), "V")
    dimension = (15, 15)
    assert verify_board_boundaries(coup, dimension) is True


def test_verif_bornes_fails_vertically() -> None:
    """Test that verify_board_boundaries returns False for an invalid vertical word placement."""
    coup = ("BONJOUR", (10, 7), "V")
    dimension = (15, 15)
    assert verify_board_boundaries(coup, dimension) is False


def test_verif_bornes_fails_horizontally() -> None:
    """Test that verify_board_boundaries returns False for an invalid horizontal word placement."""
    coup = ("BONJOUR", (7, 10), "H")
    dimension = (15, 15)
    assert verify_board_boundaries(coup, dimension) is False


def test_verif_premier_tour_vertically() -> None:
    """Test that verify_first_word_centered returns True for a valid vertical first word placement."""
    coup = ("BONJOUR", (7, 7), "V")
    assert verify_first_word_centered(coup) is True


def test_verif_premier_tour_horizontally() -> None:
    """Test that verify_first_word_centered returns True for a valid horizontal first word placement."""
    coup = ("BONJOUR", (7, 7), "H")
    assert verify_first_word_centered(coup) is True


def test_verif_premier_tour_fails() -> None:
    """Test that verify_first_word_centered returns False for an invalid first word placement."""
    coup = ("BONJOUR", (5, 5), "H")
    assert verify_first_word_centered(coup) is False


def test_draw_hand() -> None:
    """Test that draw_hand correctly draws tiles to fill the player's hand to 7 tiles.

    Verifies that the returned tile bag and player hand have the expected lengths, and that the correct tiles are
    removed from the tile bag and added to the player's hand.
    """
    tile_bag = "AAAAABBBBBCCCCCDDDDDEEEEE"
    player_hand = "AKDH"
    new_tile_bag, new_player_hand = draw_hand(tile_bag, player_hand)
    assert len(new_player_hand) == 7

    bag_before = Counter(tile_bag)
    bag_after = Counter(new_tile_bag)

    hand_before = Counter(player_hand)
    hand_after = Counter(new_player_hand)

    drawn_tiles = hand_after - hand_before
    removed_tiles = bag_before - bag_after

    assert drawn_tiles == removed_tiles
    for letter in player_hand:
        assert hand_after[letter] == hand_before[letter] + drawn_tiles[letter]


def test_draw_hand_empty_bag() -> None:
    """Test that draw_hand raises a ValueError when attempting to draw from an empty tile bag."""
    error_message = "Le sac de lettres est vide. Impossible de piocher."
    with pytest.raises(ValueError, match=error_message):
        draw_hand("", "ABC")
