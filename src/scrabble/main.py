import secrets
from copy import deepcopy
from pathlib import Path

from scrabble.player import Player


def load_occurrences_and_points(
    letter_occurrences_scores_file: str,
) -> tuple[dict[str, int], dict[str, int]]:
    """Open and read a letter definition file and return occurrences and points.

    The file should contain one line per letter. Each line holds a letter, the number
    of occurrences of that letter in the game, and the points awarded for that
    letter, separated by whitespace. Returns two dictionaries mapping letters to
    occurrences and letters to point values respectively.

    Args:
        letter_occurrences_scores_file (str): Path to the letters file to open.

    Returns:
        occurrence_dict (dict[str, int]): Mapping from letter to its occurrence count.
        points_dict (dict[str, int]): Mapping from letter to its point value.

    Example:
        # If the file "letters.txt" contains the line "A 15 1":
        >>> load_occurrences_and_points("letters.txt")
        ({"A": 15}, {"A": 1})

    """
    occurrence_dict: dict[str, int] = {}
    points_dict: dict[str, int] = {}

    with Path(letter_occurrences_scores_file).open(encoding="utf-8") as file:
        for line in file:
            lettre, occurrence, points = line.split()
            occurrence_dict[lettre] = int(occurrence)
            points_dict[lettre] = int(points)

    return occurrence_dict, points_dict


def initialise_tile_bag(letter_occurrence_mapping: dict[str, int]) -> str:
    """Return the initial tile bag as a sorted string of letters.

    Builds a string containing each letter repeated according to its occurrence
    count and returns the letters sorted alphabetically.

    Args:
        letter_occurrence_mapping (dict[str, int]): Mapping from letter to number of
            occurrences to include in the initial bag.

    Returns:
        sorted_characters (str): String with all letters for the bag, sorted.

    Example:
        >>> letter_occurrence_mapping = {'E':5, 'A':7}
        >>> initialise_tile_bag(letter_occurrence_mapping)
        'AAAAAAAEEEEE'

    """
    sorted_characters = "".join(
        sorted(lettre * letter_occurrence_mapping[lettre] for lettre in letter_occurrence_mapping),
    )

    return sorted_characters


def initialise_board(dimensions: tuple[int, int]) -> list[list[str]]:
    """Create and return an empty game board of given dimensions.

    The board is represented as a list of rows, each a list of strings. Empty
    squares are filled with the underscore character "_".

    Args:
        dimensions: Tuple of (number_of_lines, number_of_columns).

    Returns:
        board: The initialized board.

    Example:
        >>> initialise_board((3, 4))
        [["_", "_", "_", "_"], ["_", "_", "_", "_"], ["_", "_", "_", "_"]]

    """
    lines, columns = dimensions
    board = [["_" for _ in range(columns)] for _ in range(lines)]
    return board


def ask_word() -> tuple[str, tuple[int, int], str]:
    """Ask the player for where and what word they want to place.

    Returns:
        word (str): Uppercase word to place.
        position (tuple[int, int]): (row, column) index for the first letter.
        direction (str): 'H' for horizontal or 'V' for vertical.

    Example (interactive):
        >>> ask_word()
        Sure quelle ligne voulez-vous placer votre première lettre? 5
        Sure quelle colonne voulez-vous placer votre première lettre? 6
        Dans quelle direction voulez-vous placer votre mot? (h ou v) h
        Quelle mot voulez-vous placer? Bonjour
        ('BONJOUR', (5, 6), 'H')

    """
    line = get_position("ligne")
    column = get_position("colonne")
    direction = get_direction()
    word = get_word()
    position = (line, column)
    return word, position, direction


def get_word() -> str:
    """Retrieve the word the player wants to play and return it in uppercase.

    Keeps prompting until an alphabetic word is provided.

    Returns:
        The proposed word in uppercase.

    """
    word = "-1"
    while not word.isalpha():
        word = input("Quel mot proposez vous? ")

    return word.upper()


def get_direction() -> str:
    """Prompt the player for a direction and return 'H' or 'V'.

    Returns:
        The direction chosen by the player ('H' or 'V').

    """
    direction = "-1"
    while direction not in {"V", "H", "v", "h"}:
        direction = input("Donnez la direction (h = horizontal, v = vertical) ")

    return direction.upper()


def get_position(axe: str) -> int:
    """Prompt for a row or column index (0-14) and return it as int.

    Args:
        axe (str): The axis name to show in the prompt ('ligne' or 'colonne').

    """
    position = "-1"
    while not position.isdigit() or not 0 <= int(position) <= 14:  # noqa: PLR2004
        position = input(f"Numéro de {axe} de la première lettre de votre mot ")

    return int(position)


def verify_board_boundaries(
    move: tuple[str, tuple[int, int], str],
    dimensions: tuple[int, int],
) -> bool:
    """Return True if the word fits within the board boundaries, else False.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        dimensions: (number_of_lines, number_of_columns)

    """
    word, position, direction = move
    line, column = position
    lines, columns = dimensions
    word_length = len(word)
    if (direction == "V" and line + word_length < columns + 1) or (
        direction == "H" and column + word_length < lines + 1
    ):
        res = True
    else:
        res = False
    return res


def verify_first_word_centered(move: tuple[str, tuple[int, int], str]) -> bool:
    """Return True if the first move passes through the center square (7,7).

    Assumes the board is empty and the word fits on the board.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word

    Returns:
        True if the word passes through the center square; False otherwise.

    """
    word, position, direction = move
    line, column = position
    word_length = len(word)
    if (column == 7 and line <= 7 and direction == "V" and line + word_length >= 7) or (  # noqa: PLR2004
        line == 7 and column <= 7 and direction == "H" and column + word_length >= 7  # noqa: PLR2004
    ):
        res = True
    else:
        res = False
    return res


def draw_hand(tile_bag: str, player_hand: str) -> tuple[str, str]:
    """Randomly draw tiles from the bag to fill the player's rack to 7 tiles.

    Args:
        tile_bag (str): String representing the bag letters, sorted alphabetically.
        player_hand (str): String representing the player's current rack letters.

    Returns:
        (tile_bag, player_hand): Updated bag string and updated player rack.

    Raises:
        ValueError: If the tile bag is empty.

    Example:
        >>> draw_hand("AAAAABBBBBCCCCCDDDDDEEEEE", "AKDH")
        ("AAAAABBBBBCCCDDDDDEEEE", "AKDHCEC")  # example result (random)

    """
    if tile_bag == "":
        error_message = "Le sac de lettres est vide. Impossible de piocher."
        raise ValueError(error_message)
    for _ in range(7 - len(player_hand)):
        x = secrets.randbelow(len(tile_bag))
        player_hand += tile_bag[x]
        tile_bag = tile_bag[:x] + tile_bag[x + 1 :]
    return tile_bag, player_hand


def verify_player_hand_against_move(
    board: list[list[str]],
    player_hand: str,
    move: tuple[str, tuple[int, int], str],
) -> bool:
    """Return True if the player has the letters needed for the word.

    This also returns True if some letters are missing from the player's rack but
    are already present on the board at the correct positions. Assumes the word
    fits within board bounds.

    Args:
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.
        player_hand: String of player's rack letters (uppercase).
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.

    Returns:
        bool: True if the player can form the word using rack letters combined
            with letters on the board; False otherwise.

    """
    word, position, direction = move
    line, column = position
    x = player_hand
    if direction == "V":
        for i in range(len(word)):
            x += board[line + i][column]
    elif direction == "H":
        for i in range(len(word)):
            x += board[line][column + i]
    x = x.replace("_", "")
    x = "".join(sorted(x))
    word = "".join(sorted(word))
    j, i = 0, 0
    while j < len(word) and i < len(x):
        if word[j] == x[i]:
            j += 1
        i += 1
    return j == len(word)


def get_dictionary_set(dictionary_file_name: str) -> set[str]:
    """Load dictionary words from a file and return them as a set.

    The file should contain one word per line.

    Args:
        dictionary_file_name (str): Path to the dictionary text file.

    Returns:
        set[str]: Set of words loaded from the file.

    """
    dictionary = set()
    with Path(dictionary_file_name).open(encoding="utf-8") as file:
        for line in file:
            word = line.strip()
            dictionary.add(word)
    return dictionary


def verify_word(word: str, set_of_valid_words: set[str]) -> bool:
    """Return True if the given word is present in the dictionary set.

    Args:
        word: Word to check (uppercase).
        set_of_valid_words: Set of valid words.

    """
    return word in set_of_valid_words


def verify_word_placement(
    move: tuple[str, tuple[int, int], str],
    board: list[list[str]],
) -> bool:
    """Return True if placing the word doesn't conflict with existing letters on board.

    The function checks that any existing letter on the board at the placement
    positions matches the corresponding letter in the word. Assumes word fits in
    board bounds.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    """
    word, position, direction = move
    line, column = position
    new_word = ""
    x = 0
    if direction == "H":
        for i in range(len(word)):
            new_word += board[line][column + i]
    elif direction == "V":
        for i in range(len(word)):
            new_word += board[line + i][column]
    for z in range(len(new_word)):
        if new_word[z] == "_" or new_word[z] == word[z]:
            x += 1
    return x == len(word)


def check_word_accepted(  # noqa: C901, PLR0912, PLR0913, PLR0915
    board: list[list[str]],
    player_hand: str,
    move: tuple[str, tuple[int, int], str],
    set_of_valid_words: set[str],
    turn: int,
    dimensions: tuple[int, int],
) -> bool:
    """Return True if the proposed move is acceptable according to game rules.

    The function validates a combination of checks depending on whether this is
    the first turn or later turns. It uses the helper functions that test bounds,
    dictionary membership, rack letters, placement conflicts, and perpendicular
    words.

    Args:
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.
        player_hand: Player's rack letters.
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        set_of_valid_words: Set of valid words.
        turn: Current turn number (1 means first turn).
        dimensions: Board dimensions.

    Returns:
        bool: True if move is valid and accepted; False otherwise. Prints messages
            explaining the rejection reason(s).

    Example:
        >>> board = [
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ]
        >>> set_of_valid_words = [{'K', 'C', 'A'}, {'SI', 'DE'}, {'SES', 'DES'}]
        >>> player_hand = "PRDSUET"
        >>> move = ("DES", (7,7), "H")
        >>> turn = 1
        >>> dimensions = (15,15)
        >>> check_word_accepted(board, player_hand, move, set_of_valid_words, turn, dimensions)
        True

    """
    word, position, direction = move
    in_bounds = verify_board_boundaries((word, position, direction), dimensions)
    res = True
    if in_bounds and turn == 1:
        ve_prem = verify_first_word_centered((word, position, direction))
        ve_lettre = verify_player_hand_against_move(
            board,
            player_hand,
            (word, position, direction),
        )
        ve_mot = verify_word(word, set_of_valid_words)
        ve_emp = verify_word_placement((word, position, direction), board)
        if not ve_prem or not ve_lettre or not ve_mot or not ve_emp:
            if not ve_lettre:
                print(
                    "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer.",
                )
            if not ve_mot:
                print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
            if not ve_emp:
                print(
                    "Désolé mais votre mot entre en conflict avec des lettre du plateau. Veuillez réessayer.",
                )
            if not ve_prem:
                print(
                    "Désolé mais le premier mot doit passer par la case centrale. Veuillez réessayer.",
                )
            res = False
    elif in_bounds:
        ve_lettre = verify_player_hand_against_move(
            board,
            player_hand,
            (word, position, direction),
        )
        ve_mot = verify_word(word, set_of_valid_words)
        ve_emp = verify_word_placement((word, position, direction), board)
        len_perp = len(get_perpendicular_words(move, board, set_of_valid_words))
        ut_plateau = use_board_letters(move, board)
        if len_perp == 1:
            if not ve_lettre or not ve_mot or not ve_emp or not ut_plateau:
                if not ve_lettre:
                    print(
                        "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer.",
                    )
                if not ve_mot:
                    print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
                if not ve_emp:
                    print(
                        "Désolé mais votre mot entre en conflict avec des lettre du plateau. Veuillez réessayer.",
                    )
                if not ut_plateau:
                    print(
                        "Désolé mais votre mot ne se base sure aucun autre mot du plateau. Veuillez réessayer.",
                    )
                res = False
        elif len_perp > 1:
            if not ve_lettre or not ve_mot or not ve_emp:
                if not ve_lettre:
                    print(
                        "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer.",
                    )
                if not ve_mot:
                    print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
                if not ve_emp:
                    print(
                        "Désolé mais votre mot entre en conflict avec des lettre du plateau. Veuillez réessayer.",
                    )
                res = False
        elif len_perp == 0:
            print(
                "Le mot créent des mots perpendicular qui n'existe pas. Veuillez réessayer.",
            )
            res = False
    else:
        if not in_bounds:
            print("le mot n'entre pas dans les bornes du plateau. Veuillez réessayer.")
        res = False
    return res


def compute_score(word: list[str], letter_points_mapping: dict[str, int]) -> int:
    """Compute the total score for a list of words.

    Args:
        word: List of words formed (strings).
        letter_points_mapping: Mapping from letter to its points value.

    Returns:
        int: Total points for all provided words.

    """
    points = 0
    for i in range(len(word)):
        for x in range(len(word[i])):
            points += letter_points_mapping[word[i][x]]
    return points


def place_word(move: tuple[str, tuple[int, int], str], board: list[list[str]]) -> str:
    """Place the word on the board and return letters that were already present.

    This function does not remove letters from the player's rack; it only
    returns the letters that were already on the board at the placement
    positions so the caller can avoid removing them from the rack.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    Returns:
        Concatenation of letters that were already present on the board at the placement positions.

    Example:
        >>> board = [
            ["_", "_", "A","R"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
        ]
        >>> word = "BAR"
        >>> position = (0,1)
        >>> direction = "H"
        >>> move = word,position,direction
        >>> extra_letters = place_word(board,move)
        >>> print(board)
        >>> [
            ["_", "B", "A","R"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
        ]
        >>> print(extra_letters)
        >>> "AR"

    """
    word, position, direction = move
    line, column = position
    extra_letters = ""
    if direction == "V":
        for i in range(len(word)):
            if board[line + i][column] != "_":
                extra_letters += board[line + i][column]
    elif direction == "H":
        for i in range(len(word)):
            if board[line][column + i] != "_":
                extra_letters += board[line][column + i]
    return extra_letters


def remove_used_letters_from_player_hand(
    player_hand: str,
    word: str,
    extra_letters: str,
) -> str:
    """Remove the letters used to form the played word from the player's rack.

    The function takes into account letters already present on the board
    (provided in `extra_letters`) and will not remove those from the rack.

    Args:
        player_hand: Player's rack string (uppercase).
        word: Word placed.
        extra_letters: Letters already present on the board at placement
            positions (should not be removed from the rack).

    Returns:
        Updated rack string after removing used letters.

    Examples:
        >>> player_hand = "AHDBJTE"
        >>> extra_letters = "B"
        >>> word = "BAH"
        >>> remove_used_letters_from_player_hand(player_hand, word, extra_letters)
        DBJTE

    """
    for i in range(len(extra_letters)):
        word = word.replace(extra_letters[i], "", 1)
    for x in range(len(word)):
        player_hand = player_hand.replace(word[x], "", 1)
    return player_hand


def update_board_with_move(
    move: tuple[str, tuple[int, int], str],
    board: list[list[str]],
) -> list[list[str]]:
    """Update the board with the player's move and return the updated board.

    Args:
        move: a 3-uple composed of
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    Returns:
        list of sublists representing each row of the game board. Each sublist contains either an underscore to indicate
        an empty cell, or a capital letter if it has already been placed there.

    Example:
        >>> move = ("DES", (7,7), "H")
        >>> board = [
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ]
        >>> update_board_with_move(coup, plateau)
        [
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","D","E","S","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ]

    """
    word, position, direction = move
    line, column = position
    if direction == "H":
        for i in range(len(word)):
            board[line][column + i] = word[i]
    elif direction == "V":
        for i in range(len(word)):
            board[line + i][column] = word[i]
    return board


def multiplayer() -> list[Player]:
    """Returns a list of players for a multiplayer game.

    Returns:
        The list of players.

    Examples:
        >>> multiplayer()
        Combien de joueur êtes vous?
        1
        Quel est le nom du joueur n° 1 ?
        Sébastien
        [["Sébastien", "", 0]]

    """
    number_of_players = "-1"
    while not number_of_players.isdigit():
        number_of_players = input("Combien de joueur êtes vous? ")
    number_of_players_int = int(number_of_players)

    list_of_players = [Player(input(f"Quel est le nom du joueur n°{i + 1} ? ")) for i in range(number_of_players_int)]

    return list_of_players


def display_board(board: list[list[str]]) -> None:
    """Display the game board in a readable format.

    Args:
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    Examples:
        >>> board = [
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
            ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ]
        >>> affichage_plateau(plateau)
             0    1    2    3    4    5    6    7    8    9   10   11   12   13   14
        0  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 0
        1  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 1
        2  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 2
        3  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 3
        4  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 4
        5  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 5
        6  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 6
        7  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 7
        8  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 8
        9  ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 9
        10 ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 10
        11 ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 11
        12 ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 12
        13 ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 13
        14 ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'] 14
             0    1    2    3    4    5    6    7    8    9   10   11   12   13   14

    """
    print(
        "     0    1    2    3    4    5    6    7    8    9   10   11   12   13   14",
    )
    for x in range(len(board)):
        if x > 9:  # noqa: PLR2004
            print(x, board[x], x)
        else:
            print(x, "", board[x], x)
    print(
        "     0    1    2    3    4    5    6    7    8    9   10   11   12   13   14",
    )


def use_board_letters(
    move: tuple[str, tuple[int, int], str],
    board: list[list[str]],
) -> bool:
    """Return True if the word to place uses one or more letters already on the board.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    Returns:
        True if at least one letter of the word to place overlaps with an existing letter on the board; False otherwise.

    Examples:
    >>> plateau = [
        ["_", "_", "A","R"],
        ["_", "_", "_","_"],
        ["_", "_", "_","_"],
        ["_", "_", "_","_"],
    ]
    >>> mot = "BAR"
    >>> position = (0,1)
    >>> direction = "H"
    >>> coup = mot,position,direction
    >>> utilise_lettre_plateau(coup, plateau)
    True

    """
    res = True
    if len(place_word(move, board)) == 0:
        res = False
    return res


def get_perpendicular_words(  # noqa: C901, PLR0912
    move: tuple[str, tuple[int, int], str],
    board: list[list[str]],
    set_of_valid_words: set[str],
) -> list[str]:
    """Return a list of new words formed perpendicular to the placed word.

    When placing a word on the board, it is possible that it is adjacent to letters already present on the board.
    New words perpendicular to the word being placed are then formed.
    3 cases are possible:
        - If no perpendicular words are formed, this function returns a list containing one element: the word to be
            placed.
        - If there are perpendicular words and they ALL belong to the dictionary, this function returns the list
            containing all the new words formed (the word to be placed and the new perpendicular words), sorted in
            alphabetical order.
        - If there are perpendicular words and at least one of them does not exist in the dictionary, the function
            returns an empty list [].

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.
        set_of_valid_words (set): set of all valid words.

    Returns:
        list of words depending on the 3 cases described in de summary.

    Examples:
        >>> move = ('DENI', (8, 7), 'H')
        >>> board = [
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', 'R', 'A', 'P', 'E', 'E', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
            ['_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_', '_'],
        ]
        >>> set_of_valid_words = [{'A', 'K', 'C'}, {'DE', 'SI', 'RE', 'AN', 'PI'}, {'DES', 'SES'},
                {'DOIS', 'CRUS', 'MAIS', 'VOIS', 'DENI'}, {'MARRE', 'BRASE', 'DOIGT', 'CRABE'}, {'PIQUEE', 'DOIGTS'}]
        >>> get_perpendicular_words(move, board, set_of_valid_words)
        []

    """
    word, position, direction = move
    line, column = position
    a, b = position
    d = 0
    new_word = ""
    liste_mots_perpendicular = []
    lettre_deja_presente = get_existing_letter_positions(move, board)
    plateau_test = deepcopy(board)
    plateau_test = update_board_with_move(move, plateau_test)
    if direction == "V":
        for i in range(len(word)):
            for x in range(len(lettre_deja_presente)):
                if (line + i, column) == lettre_deja_presente[x]:
                    d += 1
            while plateau_test[a + i][b] != "_" and b > 0 and d == 0:
                b -= 1
            b += 1
            while plateau_test[a + i][b] != "_" and b < 14 and d == 0:  # noqa: PLR2004
                new_word += plateau_test[a + i][b]
                b += 1
            if len(new_word) > 1:
                liste_mots_perpendicular.append(new_word)
            new_word = ""
            a, b = position
            d = 0
    elif direction == "H":
        for i in range(len(word)):
            for x in range(len(lettre_deja_presente)):
                if (line, column + i) == lettre_deja_presente[x]:
                    d += 1
            while plateau_test[a][b + i] != "_" and a > 0 and d == 0:
                a -= 1
            a += 1
            while plateau_test[a][b + i] != "_" and a < 14 and d == 0:  # noqa: PLR2004
                new_word += plateau_test[a][b + i]
                a += 1
            if len(new_word) > 1:
                liste_mots_perpendicular.append(new_word)
            new_word = ""
            a, b = position
    liste_mots_perpendicular.append(word)
    if len(liste_mots_perpendicular) > 1:
        for test in liste_mots_perpendicular:
            if not verify_word(test, set_of_valid_words):
                liste_mots_perpendicular = []
    liste_mots_perpendicular.sort()
    return liste_mots_perpendicular


def get_existing_letter_positions(
    move: tuple[str, tuple[int, int], str],
    board: list[list[str]],
) -> list[tuple[int, int]]:
    """Return the positions of letters already present on the board at the placement.

    Args:
        move: a 3-uple composed of:
            word: capitalized string representing the word to place.
            position: integer tuple (l,c) which indicate the line number (l) and column number (c) of the first letter
                of the word to place.
            direction: a character (h or v) indicating the direction of the word.
        board: a list of sublists representing each row of the game board. Each sublist contains either an underscore to
            indicate an empty cell, or a letter if it has already been placed there.

    Returns:
        position (list): une liste de tuple correspondent aux positions des lettres déjà présentes sure le plateau à
            l'emplacement du mot qui va être placé.

    Examples:
    >>> move = ("DES", (6,7), "V")
    >>> board = [
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","E","S","P","O","I","R","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
        ["_","_","_","_","_","_","_","_","_","_","_","_","_","_","_"],
    ]
    >>> get_existing_letter_positions(move, board)
    [(7,7)]

    """
    word, position, direction = move
    line, column = position
    position = []
    if direction == "V":
        for i in range(len(word)):
            if board[line + i][column] != "_":
                position.append((line + i, column))
    elif direction == "H":
        for i in range(len(word)):
            if board[line][column + i] != "_":
                position.append((line, column + i))
    return position


def fifty_points(mot: str, extra_letters: str) -> int:
    """Return 50 if the player used all rack tiles this turn (a Scrabble), else 0.

    Args:
        mot: Word played.
        extra_letters: Letters already present on the board at the placement
            positions (these do not consume rack tiles).

    Returns:
        points (int): entier valant 50 si toutes les lettre du chevalet sont utilisées en un coup, 0 dans le cas
            contraire

    Examples:
        >>> mot = "BONJOUR"
        >>> lettre_ en_plus = ""
        >>> fifty_points(mot, lettre_en_plus)
        50

    """
    x = len(extra_letters)
    if len(mot) > x + 6:
        points = 50
        print("Scrabble !")
    else:
        points = 0
    return points


def run() -> None:
    """Run the interactive Scrabble game loop.

    Orchestrates player turns, drawing tiles, prompting for moves, validating
    and applying them, and updating scores until the bag is empty.
    """
    players = multiplayer()
    turn = 1
    dimensions = (15, 15)
    board = initialise_board(dimensions)
    letter_occurrence_mapping, letter_points_mapping = load_occurrences_and_points(
        "resources/Lettres.txt",
    )
    set_of_valid_words = get_dictionary_set("resources/dico.txt")
    tile_bag = initialise_tile_bag(letter_occurrence_mapping)
    while len(tile_bag) > 0:
        for player in players:
            display_board(board)
            tile_bag, player.hand = draw_hand(tile_bag, player.hand)
            print("C'est au tour de", player.name)
            print("Vous avez dans votre main les jetons suivants:", player.hand)
            word, position, direction = ask_word()
            while not check_word_accepted(
                board,
                player.hand,
                (word, position, direction),
                set_of_valid_words,
                turn,
                dimensions,
            ):
                word, position, direction = ask_word()
            extra_letters = place_word((word, position, direction), board)
            potential_fifty_points = fifty_points(word, extra_letters)
            pts_scrabble_this_round = compute_score(
                get_perpendicular_words(
                    (word, position, direction),
                    board,
                    set_of_valid_words,
                ),
                letter_points_mapping,
            )
            player.score += pts_scrabble_this_round + potential_fifty_points
            print(
                "Tu viens de marquer",
                pts_scrabble_this_round + potential_fifty_points,
                "points.",
            )
            print("Tu as au total", player.score, "points.")
            player.hand = remove_used_letters_from_player_hand(
                player.hand,
                word,
                extra_letters,
            )
            board = update_board_with_move((word, position, direction), board)
            turn += 1
