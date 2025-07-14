from pytest import MonkeyPatch

from src.scrabble.main import (
    get_direction,
    get_mot,
    get_position,
    init_pioche,
    init_plateau,
    load_fichier_lettres,
    propose_mot,
    verif_bornes,
    verif_premier_tour,
)


def test_load_fichier_lettres():
    file_name = "resources/Lettres.txt"
    expected_occurence = {
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

    occurence, points = load_fichier_lettres(file_name)

    assert expected_occurence == occurence
    assert expected_points == points


def test_pioche_init():
    occurence_lettres = {"E": 5, "A": 7}
    output = init_pioche(occurence_lettres)
    expected_output = "AAAAAAAEEEEE"
    assert output == expected_output


def test_plateau_init():
    lines, columns = 3, 4
    plateau = init_plateau((lines, columns))
    expected_plateu = [
        ["_", "_", "_", "_"],
        ["_", "_", "_", "_"],
        ["_", "_", "_", "_"],
    ]
    assert expected_plateu == plateau


def test_get_position(monkeypatch: MonkeyPatch):
    position = "5"
    all_inputs = ["dummy_Value", "-5", "30", position]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert int(position) == get_position("dummy_value")


def test_get_direction(monkeypatch: MonkeyPatch):
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


def test_get_mot(monkeypatch: MonkeyPatch):
    mot = "hello"
    all_inputs = ["123", "hey1", mot]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    assert mot.upper() == get_mot()


def test_propose_mot(monkeypatch: MonkeyPatch):
    all_inputs = ["5", "5", "H", "hello"]
    monkeypatch.setattr("builtins.input", lambda _: all_inputs.pop(0))
    expected_output = ("HELLO", (5, 5), "H")
    assert expected_output == propose_mot()


def test_verif_bornes_passes_horizontally():
    coup = ("BONJOUR", (7, 7), "H")
    dimension = (15, 15)
    assert verif_bornes(coup, dimension) is True


def test_verif_bornes_passes_vertically():
    coup = ("BONJOUR", (7, 7), "V")
    dimension = (15, 15)
    assert verif_bornes(coup, dimension) is True


def test_verif_bornes_fails_vertically():
    coup = ("BONJOUR", (10, 7), "V")
    dimension = (15, 15)
    assert verif_bornes(coup, dimension) is False


def test_verif_bornes_fails_horizontally():
    coup = ("BONJOUR", (7, 10), "H")
    dimension = (15, 15)
    assert verif_bornes(coup, dimension) is False


def test_verif_premier_tour_vertically():
    coup = ("BONJOUR", (7, 7), "V")
    assert verif_premier_tour(coup) is True


def test_verif_premier_tour_horizontally():
    coup = ("BONJOUR", (7, 7), "H")
    assert verif_premier_tour(coup) is True


def test_verif_premier_tour_fails():
    coup = ("BONJOUR", (5, 5), "H")
    assert verif_premier_tour(coup) is False
