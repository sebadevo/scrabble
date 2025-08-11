import random
from copy import deepcopy

from scrabble.player import Player


def load_occurrences_and_points(
    nom_fichier_lettres: str,
) -> tuple[dict[str, int], dict[str, int]]:
    """
    Cette fonction ouvre et lit un fichier texte dont le nom est fourni en argument. Ce fichier contient 26 lignes
    (une pour chaque lettre de l'alphabet). Chaque ligne est composée d'une lettre, d'un nombre d'occurrences de cette
    lettre dans le jeu et des points que la lettre rapporte au joueur s'il la place, chacun séparé par un espace. Elle
    renvoie ensuite deux dictionnaires dont les clés sont les lettres contenues dans le fichier texte et les valeurs
    sont respectivement le nombre d'occurrences et les points que la lettre rapporte.

    Args:
        nom_fichier_lettres (str) : Un chaine de caractère qui représente le nom du fichier texte à ouvrir.

    Returns:
        occurence_dict (dict[str, int]) : Un dictionnaire avec comme clés les lettres contenues dans le fichier et comme valeur le nombre
            d'occurrences de cette lettre.
        points_dict (dict[str, int]) : Un dictionnaire avec comme clés les lettres contenues dans le fichier et comme valeur les points
            associés à chaque lettre.

    Examples:
        Imaginons ici que le texte à ouvrir aie "A 15 1" d'écrit et que le nom du fichier s'appelle "texte".
        >>> load_fichier_lettres(texte)
        {"A" : 15} {"A" : 1}
    """
    occurence_dict: dict[str, int] = {}
    points_dict: dict[str, int] = {}
    for line in open(nom_fichier_lettres, encoding="utf-8"):
        lettre, occurence, points = line.split()
        occurence_dict[lettre] = int(occurence)
        points_dict[lettre] = int(points)

    return occurence_dict, points_dict


def init_pioche(occurence_lettres: dict[str, int]) -> str:
    """
    Cette fonction renvoie une chaine de caractères (str) contenant toutes les lettres disponibles lors de
    l'initialisation du jeu, classées dans l'ordre alphabétique.

    Args:
        occurences_lettres (dict[str, int]) : dictionnaire ayant comme clés toutes les lettres de l'alphabet et comme valeur, le
            nombre de fois (int) que chaque lettre devra être ajoutée à la pioche

    Returns:
        sorted_characters (str) : une chaine de caractère contenant toutes les lettres de la pioche classées dans l'ordre alphabétique.

    Examples:
        >>> occurence_lettres = {'E':5, 'A':7}
        >>> pioche_init(occurence_lettres)
        AAAAAAAEEEEE
    """
    sorted_characters = "".join(
        sorted(lettre * occurence_lettres[lettre] for lettre in occurence_lettres)
    )

    return sorted_characters


def init_board(dimensions: tuple[int, int]) -> list[list[str]]:
    """
    Crée le plateau de jeu. Le plateau de jeu consiste en une liste de number_of_lines sous-listes, chacune de longueur
    number_of_columns, où chaque élément représente une case du plateau vide grâce à la valeur "_"
    (underscore).

    Args:
        dimensions (tuple[int, int]) : un tuple de deux nombres entiers et positifs, respectivement le nombre de lignes
            et de colonnes.

    Returns:
        plateau (list[list[str]]) : la liste de sous-listes qui représente le plateau

    Examples:
        >>> a = (3,4)
        >>> plateau_init(a)
        [["_", "_", "_", "_"], ["_", "_", "_", "_"], ["_", "_", "_", "_"]]
    """
    number_of_lines, number_of_columns = dimensions
    plateau: list[list[str]] = [
        ["_" for _ in range(number_of_columns)] for _ in range(number_of_lines)
    ]

    return plateau


def propose_mot() -> tuple[str, tuple[int, int], str]:
    """
    Cette fonction demande au joueur où et quel mot il désire placer.

    Returns:
        mot (str): Une chaine de caractère en MAJUSCULE qui indique le mot à placer.
        position (tuple[int, int]): Un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la
            colonne (c) de la première lettre du mot à placer.
        direction (str): Un charactère ("H" ou "V") qui indique la direction du mot.

    Examples:
        >>> propose_mot()
        Sur quelle ligne voulez-vous placer votre première lettre? 5
        Sur quelle colonne voulez-vous placer votre première lettre? 6
        Dans quelle direction voulez-vous placer votre mot? (h ou v) h
        Quelle mot voulez-vous placer? Bonjour
        ('BONJOUR', (5, 6), 'H')
    """
    position_ligne = get_position("ligne")
    position_colonne = get_position("colonne")
    direction = get_direction()
    mot = get_mot()
    position = (position_ligne, position_colonne)
    return mot, position, direction


def get_mot() -> str:
    """Récupère le mot que le joueur veut jouer.

    Returns:
        str: Le mot du joueur en majuscule.
    """
    mot = "-1"
    while not mot.isalpha():
        mot = input("Quel mot proposez vous? ")

    return mot.upper()


def get_direction() -> str:
    """Récupère la direction dansa laquelle le joueur veut placer son mot.

    Returns:
        str: La direction, soit 'H', soit 'V'.
    """
    direction = "-1"
    while direction not in {"V", "H", "v", "h"}:
        direction = input("Donnez la direction (h = horizontal, v = vertical) ")

    return direction.upper()


def get_position(axe: str) -> int:
    """Récupère la position ou le jouer veut placer son mot.

    Args:
        axe (str): L'axe sur lequel on va demander la position.

    Returns:
        int: La position.
    """
    position = "-1"
    while not position.isdigit() or not 0 <= int(position) <= 14:
        position = input(f"Numéro de {axe} de la première lettre de votre mot ")

    return int(position)


def verif_bornes(
    coup: tuple[str, tuple[int, int], str], dimensions: tuple[int, int]
) -> bool:
    """
    Cette fonction renvoie True si le mot à placer ne dépasse pas les des bornes du plateau de jeu. False, sinon.

    Args :
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot
        - dimensions (tuple) : un tuple de deux nombres entiers et positifs. Le premier élément est le nombre de lignes
        (nb_lignes); le deuxième élément est le nombre de colonnes (nb_colonnes)

    Returns :
        - bool: Si le mot respect les bornes du plateau.

    Examples :
        coup = ("BONJOUR", (7,7), "V")
        dimension = (15,15)
        >>> verif_bornes(coups,dimensions):
        True
    """
    word, position, direction = coup
    line, column = position
    lines, columns = dimensions
    word_length = len(word)
    if direction == "V" and line + word_length < columns + 1:
        res = True
    elif direction == "H" and column + word_length < lines + 1:
        res = True
    else:
        res = False
    return res


def verif_premier_tour(coup: tuple[str, tuple[int, int], str]) -> bool:
    """
    Cette fonction retourne True si le mot à placer passe bien par la case (7,7).On considère que le mot à placer ne
    dépasse pas des bornes du plateau et ne fait pas plus de 7 lettres. On considère également que cette fonction ne
    sera appelée qu'au premier tour. Le plateau est donc totalement vide.

    Args :
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l),et le numéro de la colonne (c)
             de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot

    Returns :
        - bool : True ou False

    Examples :
        coup = ("BONJOUR", (7,5), "V")
        >>> verif_premeier_tour(coup)
        True
    """
    word, position, direction = coup
    line, column = position
    word_length = len(word)
    if column == 7 and line <= 7 and direction == "V" and line + word_length >= 7:
        res = True
    elif line == 7 and column <= 7 and direction == "H" and column + word_length >= 7:
        res = True
    else:
        res = False
    return res


def draw_hand(pioche_jeu: str, main_joueur: str) -> tuple[str, str]:
    """
    Cette fonction choisit aléatoirement des lettre dans la pioche et les rajoute dans le chevalet du joueur jusqu'à ce
    qu'il ait 7 jetons. Elle renvoie ensuite le chevalet du joueur plein et la pioche avec les jetons en moins qui ont
    été ajouter au chevalet du joueur.

    Args:
        pioche_jeu (str) : une chaine de caractère contenant toutes les lettres de la pioche classées dans l'ordre
            alphabétique.
        Main_joueur (str) : une chaine de caractère contenant les lettre du chevalet du joueur

    Returns:
        pioche_jeu (str) : une chaine de caractère contenant toutes les lettres de la pioche mis à jour classées
            dans l'ordre alphabétique.
        Main_joueur (str) : une chaine de caractère contenant les lettre du chevalet du joueur mis à jour

    Examples:
        >>> main_joueur = "AKDH"
        >>> pioche_jeu = "AAAAABBBBBCCCCCDDDDDEEEEE"
        >>> jeton_joueur(pioche_jeu, main_joueur)
        AAAAABBBBBCCCDDDDDEEEE AKDHCEC
    """
    for _ in range(7 - len(main_joueur)):
        x = random.randint(0, len(pioche_jeu) - 1)
        main_joueur += pioche_jeu[x]
        pioche_jeu = pioche_jeu[:x] + pioche_jeu[x + 1 :]
    return pioche_jeu, main_joueur


def verif_lettre_joueur(
    plateau: list[list[str]],
    lettres_joueur: str,
    coup: tuple[str, tuple[int, int], str],
) -> bool:
    """
    Cette fonction renvoie True:
        - Si le mot à placer appartient au lettres du joueur (lettres_joueurs)
        - Si une ou plusieurs lettres manquent mais sont déjà placées à la place adéquate sur le plateau (plateau).

    Sinon, la fonction renvoie False.
    On présuppose que le mot ne dépasse pas des bornes du plateau

    Args :
        plateau: une liste de sous-listes qui représentent chacune une ligne du plateau de jeu.
            Elles contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a
            déjà été placée là auparavant.
        lettres_joueur: une liste qui contient chacune des lettres que le joueur possède sur son chevalet.
            Toutes ces lettres sont en MAJUSCULE.
        coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
                (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot

    Returns:
        - bool (True ou False)

    Examples :
        >>> verif_lettre_joueur([["","",""],["","",""],["","","_"]], PRMNUOT, ("MON", (1,0), "H"))
        True
    """
    word, position, direction = coup
    line, column = position
    x = lettres_joueur
    if direction == "V":
        for i in range(len(word)):
            x += plateau[line + i][column]
    elif direction == "H":
        for i in range(len(word)):
            x += plateau[line][column + i]
    x = x.replace("_", "")
    x = "".join(sorted(x))
    word = "".join(sorted(word))
    j, i = 0, 0
    while j < len(word) and i < len(x):
        if word[j] == x[i]:
            j += 1
        i += 1
    return j == len(word)


def list_dico(nom_fichier_dictionnaire: str) -> set[str]:
    """
    Cette fonction ouvre un fichier contenant tous les mots du scrabble triés par ordre alphabétique et les ajoute a un
    set.

    Argument:
        - nom_fichier_dictionnaire (fichier.txt) : un fichier .txt contenant tous les mots du scrabble triés par ordre
        alphabétique

    valeur de retour:
        - dictionary (set) : un set contenant tout les mots du dictionnaire.

    Examples:
    disons ici que le fichier contient les mots "BONJOUR", "AA", "MON" et "MES".
        >>> list_dico(nom_fichier_dictionnaire)
        {"BONJOUR", "AA", "MON" et "MES"}
    """
    dictionary = set()
    for m in open(nom_fichier_dictionnaire, encoding="utf-8"):
        t = m.strip()
        dictionary.add(t)
    return dictionary


def verif_mot(mot: str, dico: set[str]) -> bool:
    """
    Cette fonction renvoie True si le mot à placer est bien un mot du dictionnaire. False sinon.

    Args :
        - mot (str): une chaine de caractères en majuscule qui indique le mot à placer
        - dico (set[str]) : un set contenant tout les mots du dictionnaire accpeté au Scrabble.

    Returns :
        - bool (True ou False)

    Examples:
        >>> verif_mot("DES", {'K', 'C', 'A', 'SI', 'DE', 'SES', 'MIS', 'DES'})
        True
    """
    return mot in dico


def verif_emplacement(
    coup: tuple[str, tuple[int, int], str], plateau: list[list[str]]
) -> bool:
    """
    Cette fonction renvoie True si le mot à placer n'entre pas en conflit avec d'autres lettres déjà placées
    auparavant sur le plateau, qui ne correspondent pas aux lettres du mot. Sinon, la fonction renvoie False.
    On présuppose que le mot ne dépasse pas des bornes du plateau.

    Args :
        - coup (tuple[str, tuple[int, int], str]) : un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
                (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot
        - plateau (liste): une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Returns:
        validity (bool) : Si l'emplacement n'entre pas en conflit avec d'autres mot déjà présent sur le plateau.

    Examples:
        >>> verif_emplacement((MON, (2,0), "H"), [["_","_","_"],["_","_","_"],["_","_","_"]])
        True
    """
    word, position, direction = coup
    line, column = position
    new_word = ""
    x = 0
    if direction == "H":
        for i in range(len(word)):
            new_word += plateau[line][column + i]
    elif direction == "V":
        for i in range(len(word)):
            new_word += plateau[line + i][column]
    for z in range(len(new_word)):
        if new_word[z] == "_" or new_word[z] == word[z]:
            x += 1
    return x == len(word)


def mot_accepte(
    plateau: list[list[str]],
    lettres_joueur: str,
    coup: tuple[str, tuple[int, int], str],
    dictionnaire: set[str],
    tour: int,
    dimension: tuple[int, int],
) -> bool:
    """
    Cette fonction renvoie True si chacune des fonctions suivantes renvoient True:
        - verif_premier_tour (uniquement au premier tour)
        - verif_lettres_joueur
        - verif_mot
        - verif_bornes
        - verif_emplacement
        et en fonction de ce que renvoie la fonction mot_perpendiculaire, on test ou pas la fonction
        utilise_lettre_plateau qui est également un bool.
    Sinon, la fonction renvoie False.

    Args :
        - lettres_joueur (liste) : une liste contenant les lettres du joueur
        - plateau (liste): une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot
        - tour (int) : un entier qui représente le tour du jeu (tour = 1 représente le premier tour)
        - dictionnaire (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur
         (i+1). Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.
        - dimension (tuple) : un tuple d'entiers (nb_l, nb_c) qui indique le nombre de ligne et de colonne du plateau.

    Returns :
        - bool (True ou False)

    Examples :
        >>> plateau = [
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
        >>> dictionnaire = [{'K', 'C', 'A'}, {'SI', 'DE'}, {'SES', 'MIS', 'DES'}]
        >>> lettres_joueur = "PRDSUET"
        >>> coup = ("DES", (7,7), "H")
        >>> tour = 1
        >>> dimension = (15,15)
        >>> mot_accepte(plateau, lettres_joueur, coup, dictionnaire, tour, dimension)
        True
    """
    word, position, direction = coup
    in_bounds = verif_bornes((word, position, direction), dimension)
    res = True
    if in_bounds and tour == 1:
        ve_prem = verif_premier_tour((word, position, direction))
        ve_lettre = verif_lettre_joueur(
            plateau, lettres_joueur, (word, position, direction)
        )
        ve_mot = verif_mot(word, dictionnaire)
        ve_emp = verif_emplacement((word, position, direction), plateau)
        if not ve_prem or not ve_lettre or not ve_mot or not ve_emp:
            if not ve_lettre:
                print(
                    "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer."
                )
            if not ve_mot:
                print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
            if not ve_emp:
                print(
                    "Désolé mais votre mot entre en conflit avec des lettre du plateau. Veuillez réessayer."
                )
            if not ve_prem:
                print(
                    "Désolé mais le premier mot doit passer par la case centrale. Veuillez réessayer."
                )
            res = False
    elif in_bounds:
        ve_lettre = verif_lettre_joueur(
            plateau, lettres_joueur, (word, position, direction)
        )
        ve_mot = verif_mot(word, dictionnaire)
        ve_emp = verif_emplacement((word, position, direction), plateau)
        len_perp = len(mots_perpendiculaires(coup, plateau, dictionnaire))
        ut_plateau = utilise_lettre_plateau(coup, plateau)
        if len_perp == 1:
            if not ve_lettre or not ve_mot or not ve_emp or not ut_plateau:
                if not ve_lettre:
                    print(
                        "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer."
                    )
                if not ve_mot:
                    print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
                if not ve_emp:
                    print(
                        "Désolé mais votre mot entre en conflit avec des lettre du plateau. Veuillez réessayer."
                    )
                if not ut_plateau:
                    print(
                        "Désolé mais votre mot ne se base sur aucun autre mot du plateau. Veuillez réessayer."
                    )
                res = False
        elif len_perp > 1:
            if not ve_lettre or not ve_mot or not ve_emp:
                if not ve_lettre:
                    print(
                        "Désolé mais vous n'avez pas les lettres pour écrire ce mot. Veuillez réessayer."
                    )
                if not ve_mot:
                    print("Désolé mais ce mot n'existe pas. Veuillez réessayer.")
                if not ve_emp:
                    print(
                        "Désolé mais votre mot entre en conflit avec des lettre du plateau. Veuillez réessayer."
                    )
                res = False
        elif len_perp == 0:
            print(
                "Le mot créent des mots perpendiculaire qui n'existe pas. Veuillez réessayer."
            )
            res = False
    else:
        if not in_bounds:
            print("le mot n'entre pas dans les bornes du plateau. Veuillez réessayer.")
        res = False
    return res


def compte_points(mots: list[str], points_lettres: dict[str, int]) -> int:
    """
    Cette fonction calcule et renvoie le score associé à un ou des mots

    Args :
        - mot (list) : une liste triée dont chaque élément d'indice i, est une chaine de caractère en majuscule
        représentant les mots créés sur le plateau.
        - points_lettres (dict) : un dictionnaire contenant comme clés les différentes lettres de l'alphabet,
        en majuscule; et comme valeur, les points associées à chaque lettre.

    Returns :
        - int : points associés aux mots placés.

    Examples :
        >>> mots = ["DES"]
        >>> points_lettres = {"D" : 2, "E" : 1, "S" : 1}, si on ne considère que les lettres D, E et S.
        >>> compte_points(mots, points_lettres)
        4
    """

    points = 0
    for i in range(len(mots)):
        for x in range(len(mots[i])):
            points += points_lettres[mots[i][x]]
    return points


def placer_mot(coup: tuple[str, tuple[int, int], str], plateau: list[list[str]]) -> str:
    """
    Cette fonction modifie le plateau de sorte que les lettres du mot à placer soient insérées au bon endroit dans la
    liste de sous-listes qui représente le plateau; cette fonction renvoie ensuite les lettres du mot à placer qui sont
    déjà présentes sur le plateau à l'endroit exact où cette lettre devrait être placée (et qu'il ne faut donc pas
    retirer du chevalet du joueur par la suite).

    Args:
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot
        - plateau (liste) : une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Returns:
        - str : chaine de caractères contenant les lettres déjà présentes sur le plateau à l'emplacement du mot
        (qu'il ne faut donc pas retirer du chevalet du joueur)
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
        >>> lettres_presentes = placer_mot(plateau,coup)
        >>> print(plateau)
        >>> [
            ["_", "B", "A","R"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
            ["_", "_", "_","_"],
        ]
        >>> print(lettres_presentes)
        >>> "AR"
    """
    word, position, direction = coup
    line, column = position
    extra_letters = ""
    if direction == "V":
        for i in range(len(word)):
            if plateau[line + i][column] != "_":
                extra_letters += plateau[line + i][column]
    elif direction == "H":
        for i in range(len(word)):
            if plateau[line][column + i] != "_":
                extra_letters += plateau[line][column + i]
    return extra_letters


def retirer_chevalet(main: str, mot: str, lettre_en_trop: str) -> str:
    """
    Cette fonction retire du chevalet les lettres utile pour fabriquer le mot du joueur. elle fait donc également
    attention à ne pas retirer du chevalets des lettres déjà présente sur le plateau. Elle renvoie ce même chevalet mis
    à jour.

    Args:
        - main (str) : une chaine de caractères en majuscule représentant le chevalet du joueur.
        - mot (str): une chaine de caractères en majuscule qui indique le mot à placer.
        - lettre_en_trop (str) : une chaine de caractères en majuscule qui indique les lettres déjà présente sur le
        plateau, donc celle qui ne faudra pas retirer du chevalet du joueur.

    Returns:
        - main (str) : une chaine de caractères en majuscule représentant le chevalet du joueur mis à jour.

    Examples:
        >>>  main = "AHDBJTE"
        >>> lettre_en_trop = "B"
        >>> mot = "BAH"
        >>> retirer_chevalet(main, mot, lettre_en_trop)
        DBJTE
    """
    for i in range(len(lettre_en_trop)):
        mot = mot.replace(lettre_en_trop[i], "", 1)
    for x in range(len(mot)):
        main = main.replace(mot[x], "", 1)
    return main


def mot_sur_plateau(
    coup: tuple[str, tuple[int, int], str], plateau: list[list[str]]
) -> list[list[str]]:
    """
    Cette fonction met les lettres du mot du joueur sur le plateau et renvoie le plateau mis à jour.

    Args:
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer
            - dir (str) : un charactère (h ou v) qui indique la direction du mot
        - plateau (liste): une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Returns:
        - plateau (liste): une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Examples:
        >>> coup = ("DES", (7,7), "H")
        >>> plateau = [
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
        >>> mot_sur_plateau(coup, plateau)
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
    word, position, direction = coup
    line, column = position
    if direction == "H":
        for i in range(len(word)):
            plateau[line][column + i] = word[i]
    elif direction == "V":
        for i in range(len(word)):
            plateau[line + i][column] = word[i]
    return plateau


def multijoueur() -> list[Player]:
    """
    Cette fonction renvoie une list de sous-liste chacune composé en indice:
        - 0 : le nom du joueur
        - 1 : le chevalet du joueur
        - 2 : les points du joueur
    Le nombre de sous listes correspond au nombre de joueur.

    Args :
        /

    Returns:
        - lsit_joueur (list) : une list de sous-liste correspondant au nombre de joueur.

    Examples:
        >>> multijoueur()
        Combien de joueur êtes vous?
        1
        Quel est le nom du joueur n° 1 ?
        Sebastien
        [["Sebastien", "", 0]]
    """
    number_of_players = "-1"
    while not number_of_players.isdigit():
        number_of_players = input("Combien de joueur êtes vous? ")
    number_of_players_int = int(number_of_players)

    list_of_players = [
        Player(input(f"Quel est le nom du joueur n°{i + 1} ? "))
        for i in range(number_of_players_int)
    ]

    return list_of_players


def display_board(plateau: list[list[str]]) -> None:
    """
    Cette fonction ne sert qu'à imprimer le plateau d'une manière plus esthétique. Elle ne renvoie rien.

    Args:
        - plateau (liste): une liste de sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    valeur de retour:
        /

    Examples:
        >>> plateau = [
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
        "     0    1    2    3    4    5    6    7    8    9   10   11   12   13   14"
    )
    for x in range(len(plateau)):
        if x > 9:
            print(x, plateau[x], x)
        else:
            print(x, "", plateau[x], x)
    print(
        "     0    1    2    3    4    5    6    7    8    9   10   11   12   13   14"
    )


def utilise_lettre_plateau(
    coup: tuple[str, tuple[int, int], str], plateau: list[list[str]]
) -> bool:
    """
    Cette fonction renvoie True si le mot à placer utilise une ou plusieurs lettres déjà présentes sur le plateau de
    jeu. Elle renvoie False sinon.

    Args:
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer.
            - dir (str) : un charactère ("h" ou "v") qui indique la direction du mot.
        - plateau (liste) : une liste de 15 sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Returns:
        - bool (True / False)

    Examples:
    >>>plateau = [
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
    if len(placer_mot(coup, plateau)) == 0:
        res = False
    return res


def mots_perpendiculaires(
    coup: tuple[str, tuple[int, int], str],
    plateau: list[list[str]],
    dico: set[str],
) -> list[str]:
    """
    Lorsqu'un mot est placé sur le plateau de jeu, il est possible qu'il soit adjacent à des lettres déjà présentes sur
    le plateau. De nouveaux mots perpendiculaires au mot à placer sont alors formés.
    3 cas sont possibles:
        - Si aucun mot perpendiculaire n'est formé, cette fonction renvoie une liste contenant un élément : le mot à
        placer.
        - S'il existe des mots perpendiculaires et qu'ils appartiennent TOUS au dictionnaire, cette fonction renvoie la
        liste contenant tous les nouveaux mots formés (le mot à placer et les nouveaux mots perpendiculaires), triés
        dans l'ordre alphabétique.
        - S'il existe des mots perpendiculaires et qu'au moins un d'entre eux n'existe pas dans le dictionnaire, la
        fonction renvoie une liste vide [].

    Args:
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer.
            - dir (str) : un charactère ("h" ou "v") qui indique la direction du mot.
        - plateau (liste) : une liste de 15 sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.
        - dico (dict) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur (i+1).
        Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.

    Returns:
        - liste de chaine de caractères

    Examples :
        >>> coup = ('DENI', (8, 7), 'H')
        >>> plateau = [
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
        >>> dico = [{'A', 'K', 'C'}, {'DE', 'SI', 'RE', 'AN', 'PI'}, {'DES', 'MIS', 'SES'},
                {'DOIS', 'CRUS', 'MAIS', 'VOIS', 'DENI'}, {'MARRE', 'BRASE', 'DOIGT', 'CRABE'}, {'PIQUEE', 'DOIGTS'}]
        >>> mots_perpendiculaires(coup, plateau, dico)
        []
    """
    word, position, direction = coup
    line, column = position
    a, b = position
    d = 0
    new_word = ""
    liste_mots_perpendiculaire = []
    lettre_deja_presente = localisation_lettre_sur_plateau(coup, plateau)
    plateau_test = deepcopy(plateau)
    plateau_test = mot_sur_plateau(coup, plateau_test)
    if direction == "V":
        for i in range(len(word)):
            for x in range(len(lettre_deja_presente)):
                if (line + i, column) == lettre_deja_presente[x]:
                    d += 1
            while plateau_test[a + i][b] != "_" and b > 0 and d == 0:
                b -= 1
            b += 1
            while plateau_test[a + i][b] != "_" and b < 14 and d == 0:
                new_word += plateau_test[a + i][b]
                b += 1
            if len(new_word) > 1:
                liste_mots_perpendiculaire.append(new_word)
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
            while plateau_test[a][b + i] != "_" and a < 14 and d == 0:
                new_word += plateau_test[a][b + i]
                a += 1
            if len(new_word) > 1:
                liste_mots_perpendiculaire.append(new_word)
            new_word = ""
            a, b = position
    liste_mots_perpendiculaire.append(word)
    if len(liste_mots_perpendiculaire) > 1:
        for test in liste_mots_perpendiculaire:
            if not verif_mot(test, dico):
                liste_mots_perpendiculaire = []
    liste_mots_perpendiculaire.sort()
    return liste_mots_perpendiculaire


def localisation_lettre_sur_plateau(
    coup: tuple[str, tuple[int, int], str], plateau: list[list[str]]
) -> list[tuple[int, int]]:
    """
    Cette fonction renvoie la position des lettre déjà présente sur le plateau à l'endroit où l'on va vouloir mettre un
    mot.

    Args:
        - coup (tuple): un tuple à 3 éléments:
            - mot (str): une chaine de caractère en majuscule qui indique le mot à placer
            - pos (tuple) : un tuple d'entiers (l,c) qui indiquent le numéro de ligne (l), et le numéro de la colonne
            (c) de la première lettre du mot à placer.
            - dir (str) : un charactère ("h" ou "v") qui indique la direction du mot.
        - plateau (liste) : une liste de 15 sous-listes qui représentent chacune une ligne du plateau de jeu. Elles
        contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà été
        placée là auparavant.

    Returns:
        position (list) : une liste de tuple correspondant aux positions des lettres déjà présentes sur le plateau à
            l'emplacement du mot qui va être placé.

    Examples:
    >>> coup = ("DES", (6,7), "V")
    >>> plateau = [
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
    >>> localisation_lettre_sur_plateau(coup, plateau)
    [(7,7)]
    """
    mot, pos, direc = coup
    line, column = pos
    position = []
    if direc == "V":
        for i in range(len(mot)):
            if plateau[line + i][column] != "_":
                position.append((line + i, column))
    elif direc == "H":
        for i in range(len(mot)):
            if plateau[line][column + i] != "_":
                position.append((line, column + i))
    return position


def fifty_points(mot: str, lettre_en_plus: str) -> int:
    """
    Cette fonction renvoie un entier valant 50 si toutes les lettre du chevalet sont utilisées en un coup. Elle renvoie
    un entier valant 0 si ce n'est pas le cas.

    Args:
        mot (str) : chaine de caractère correspondant au mot que le joueur à placé.
        lettre_en_plus (str) : chaine de caractère correspondant au lettre déjà présente sur le plateau à l'emplacement
        du mot que le joueur veux jouer.

    Returns:
        points (int) : entier valant 50 si toutes les lettre du chevalet sont utilisées en un coup, 0 dans le cas
            contraire

    Examples:
        >>> mot = "BONJOUR"
        >>> lettre_ en_plus = ""
        >>> fifty_points(mot, lettre_en_plus)
        50
    """
    x = len(lettre_en_plus)
    if len(mot) > x + 6:
        points = 50
        print("Scrabble !")
    else:
        points = 0
    return points


def run() -> None:
    """
    Cette fonction ne sert qu'à faire tourner tout le jeu

    Args:
        /
    Returns:
        /
    """
    players = multijoueur()
    tour = 1
    dimensions = (15, 15)
    plateau_de_jeu = init_board(dimensions)
    dico_occu, dico_points = load_occurrences_and_points("resources/Lettres.txt")
    dico_mot = list_dico("resources/dico.txt")
    pioche = init_pioche(dico_occu)
    while len(pioche) > 0:
        for player in players:
            display_board(plateau_de_jeu)
            pioche, player.hand = draw_hand(pioche, player.hand)
            print("C'est au tour de", player.name)
            print("Vous avez dans votre main les jetons suivants:", player.hand)
            mot, pos, direc = propose_mot()
            while not mot_accepte(
                plateau_de_jeu,
                player.hand,
                (mot, pos, direc),
                dico_mot,
                tour,
                dimensions,
            ):
                mot, pos, direc = propose_mot()
            lettre_en_plus = placer_mot((mot, pos, direc), plateau_de_jeu)
            pts_scrabble_fifty = fifty_points(mot, lettre_en_plus)
            pts_scrabble_this_round = compte_points(
                mots_perpendiculaires((mot, pos, direc), plateau_de_jeu, dico_mot),
                dico_points,
            )
            player.score += pts_scrabble_this_round + pts_scrabble_fifty
            print(
                "Tu viens de marquer",
                pts_scrabble_this_round + pts_scrabble_fifty,
                "points.",
            )
            print("Tu as au total", player.score, "points.")
            player.hand = retirer_chevalet(player.hand, mot, lettre_en_plus)
            plateau_de_jeu = mot_sur_plateau((mot, pos, direc), plateau_de_jeu)
            tour += 1
