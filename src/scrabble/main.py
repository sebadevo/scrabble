import random
from copy import deepcopy


def load_fichier_lettres(
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


def init_pioche(occurence_lettres: dict[str, int]):
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


def init_plateau(dimensions: tuple[int, int]) -> list[list[str]]:
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


def verif_bornes(coup, dimensions):
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
    mot, pos, direc = coup
    line, column = pos
    lignes, colonnes = dimensions
    long_mot = len(mot)
    if direc == "V" and line + long_mot < colonnes + 1:
        res = True
    elif direc == "H" and column + long_mot < lignes + 1:
        res = True
    else:
        res = False
    return res


def verif_premier_tour(coup):
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
    mot, pos, direc = coup
    li, c = pos
    long_mot = len(mot)
    if c == 7 and li <= 7 and direc == "V" and li + long_mot >= 7:
        res = True
    elif li == 7 and c <= 7 and direc == "H" and c + long_mot >= 7:
        res = True
    else:
        res = False
    return res


def jeton_joueur(pioche_jeu, main_joueur):
    """
    Cette fonction choisit aléatoirement des lettre dans la pioche et les rajoute dans le chevalet du joueur jusqu'à ce
    qu'il ait 7 jetons. Elle renvoie ensuite le chevalet du joueur plein et la pioche avec les jetons en moins qui ont
    été ajouter au chevalet du joueur.

    Args:
        - pioche_jeu (str) : une chaine de caractère contenant toutes les lettres de la pioche classées dans l'ordre
        alphabétique.
        - Main_joueur (str) : une chaine de caractère contenant les lettre du chevalet du joueur

    Valeur de retour:
        - - pioche_jeu (str) : une chaine de caractère contenant toutes les lettres de la pioche mis à jour classées
        dans l'ordre alphabétique.
        - Main_joueur (str) : une chaine de caractère contenant les lettre du chevalet du joueur mis à jour

    Examples:
        >>> main_joueur = "AKDH"
        >>> pioche_jeu = "AAAAABBBBBCCCCCDDDDDEEEEE"
        >>> jeton_joueur(pioche_jeu, main_joueur)
        AKDHCEC AAAAABBBBBCCCDDDDDEEEE
    """
    for _ in range(7 - len(main_joueur)):
        x = random.randint(0, len(pioche_jeu) - 1)
        main_joueur += pioche_jeu[x]
        pioche_jeu = pioche_jeu[:x] + pioche_jeu[x + 1 :]
    return pioche_jeu, main_joueur


def verif_lettre_joueur(plateau, lettres_joueur, coup):
    """
    Cette fonction renvoie True:
        - Si le mot à placer appartient au lettres du joueur (lettres_joueurs)
    ou
        - Si une ou plusieurs lettres manquent mais sont déjà placées à la place adéquate sur le plateau (plateau).
        Sinon, la fonction renvoie False.
    On présuppose que le mot ne dépasse pas des bornes du plateau

    Args :
        - plateau (liste) : une liste de sous-listes qui représentent chacune une ligne du plateau de jeu.
        Elles contiennent chacune, soit un underscore pour indiquer que la case est vide, soit une lettre si elle a déjà
        été placée là auparavant.
        - lettres_joueur (liste) : une liste qui contient chacune des lettres que le joueur possède sur son chevalet.
        Toutes ces lettres sont en MAJUSCULE.
        - coup (tuple): un tuple à 3 éléments:
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
    mot, pos, direc = coup
    line, column = pos
    x = lettres_joueur
    if direc == "V":
        for i in range(len(mot)):
            x += plateau[line + i][column]
    elif direc == "H":
        for i in range(len(mot)):
            x += plateau[line][column + i]
    x = x.replace("_", "")
    x = "".join(sorted(x))
    mot = "".join(sorted(mot))
    j, i = 0, 0
    while j < len(mot) and i < len(x):
        if mot[j] == x[i]:
            j += 1
        i += 1
    return j == len(mot)


def list_dico(nom_fichier_dictionnaire):
    """
    Cette fonction ouvre un fichier contenant tous les mots du scrabble triés par ordre alphabétique et les ajoute dans
    une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur (i+1). la fonction renvoie
    cette liste.

    Argument:
        - nom_fichier_dictionnaire (fichier.txt) : un fichier .txt contenant tous les mots du scrabble triés par ordre
        alphabétique

    valeur de retour:
        - dico (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur (i+1).
        Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.

    Examples:
    disons ici que le fichier contient les mots "BONJOUR", "AA", "MON" et "MES".
        >>> list_dico(nom_fichier_dictionnaire)
        [{}, {"AA"}, {"MES", "MON"}, {}, {}, {}, {"BONJOUR"}, {}, {}, {}, {}, {}, {}, {}, {}]
    """
    dico: list[set] = []
    for _ in range(15):
        dico.append(set())
    for m in open(nom_fichier_dictionnaire, encoding="utf-8"):
        t = m.strip()
        dico[len(t) - 1].add(t)
    return dico


def verif_mot(mot, dico):
    """
    Cette fonction renvoie True si le mot à placer est bien un mot du dictionnaire. False sinon.

    Args :
        - mot (str): une chaine de caractères en majuscule qui indique le mot à placer
        - dico (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur (i+1).
        Par exemple, dico[3] pointe vers un set de tous les mots à 4 lettres.

    Returns :
        - bool (True ou False)

    Examples:
        >>> verif_mot("DES", [{'K', 'C', 'A'}, {'SI', 'DE'}, {'SES', 'MIS', 'DES'}])
        True
    """
    res = False
    if len(mot) <= len(dico):
        if mot in dico[len(mot) - 1]:
            res = True
        else:
            res = False
    return res


def verif_emplacement(coup, plateau):
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
    mot, pos, direc = coup
    line, column = pos
    new_mot = ""
    x = 0
    if direc == "H":
        for i in range(len(mot)):
            new_mot += plateau[line][column + i]
    elif direc == "V":
        for i in range(len(mot)):
            new_mot += plateau[line + i][column]
    for z in range(len(new_mot)):
        if new_mot[z] == "_" or new_mot[z] == mot[z]:
            x += 1
    return x == len(mot)


def mot_accepte(plateau, lettres_joueur, coup, dictionnaire, tour, dimension):
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
    mot, pos, direc = coup
    ve_borne = verif_bornes((mot, pos, direc), dimension)
    res = True
    if ve_borne and tour == 1:
        ve_prem = verif_premier_tour((mot, pos, direc))
        ve_lettre = verif_lettre_joueur(plateau, lettres_joueur, (mot, pos, direc))
        ve_mot = verif_mot(mot, dictionnaire)
        ve_emp = verif_emplacement((mot, pos, direc), plateau)
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
    elif ve_borne:
        ve_lettre = verif_lettre_joueur(plateau, lettres_joueur, (mot, pos, direc))
        ve_mot = verif_mot(mot, dictionnaire)
        ve_emp = verif_emplacement((mot, pos, direc), plateau)
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
        if not ve_borne:
            print("le mot n'entre pas dans les bornes du plateau. Veuillez réessayer.")
        res = False
    return res


def compte_points(mots: list[str], points_lettres: dict[str, int]):
    """
    Cette fonction calcule et renvoie le score associé à un ou des mots

    Args :
        - mot (list) : une liste triée dont chaque élément d'indice i, est une chaine de caractère en majuscule
        représentant les mots créés sur le plateau.
        - points_lettres (dict) : un dictionnaire contenant comme clés les différentes lettres de l'alphabet,
        en majuscule; et comme valeur, les points associées à chaque lettre.

    Valeur de retour :
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


def placer_mot(coup, plateau):
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

    Valeur de retour:
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
    mot, pos, direc = coup
    line, column = pos
    lettre_en_trop = ""
    if direc == "V":
        for i in range(len(mot)):
            if plateau[line + i][column] != "_":
                lettre_en_trop += plateau[line + i][column]
    elif direc == "H":
        for i in range(len(mot)):
            if plateau[line][column + i] != "_":
                lettre_en_trop += plateau[line][column + i]
    return lettre_en_trop


def retirer_chevalet(main, mot, lettre_en_trop):
    """
    Cette fonction retire du chevalet les lettres utile pour fabriquer le mot du joueur. elle fait donc également
    attention à ne pas retirer du chevalets des lettres déjà présente sur le plateau. Elle renvoie ce même chevalet mis
    à jour.

    Args:
        - main (str) : une chaine de caractères en majuscule représentant le chevalet du joueur.
        - mot (str): une chaine de caractères en majuscule qui indique le mot à placer.
        - lettre_en_trop (str) : une chaine de caractères en majuscule qui indique les lettres déjà présente sur le
        plateau, donc celle qui ne faudra pas retirer du chevalet du joueur.

    Valeur de retour:
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


def mot_sur_plateau(coup, plateau):
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

    Valeur de retour:
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
    mot, pos, direc = coup
    line, column = pos
    if direc == "H":
        for i in range(len(mot)):
            plateau[line][column + i] = mot[i]
    elif direc == "V":
        for i in range(len(mot)):
            plateau[line + i][column] = mot[i]
    return plateau


def multijoueur():
    """
    Cette fonction renvoie une list de sous-liste chacune composé en indice:
        - 0 : le nom du joueur
        - 1 : le chevalet du joueur
        - 2 : les points du joueur
    Le nombre de sous listes correspond au nombre de joueur.

    Args :
        /

    Valeur de retour:
        - lsit_joueur (list) : une list de sous-liste correspondant au nombre de joueur.

    Examples:
        >>> multijoueur()
        Combien de joueur êtes vous?
        1
        Quel est le nom du joueur n° 1 ?
        Sebastien
        [["Sebastien", "", 0]]
    """
    nbr = input("Combien de joueur êtes vous? ")
    while not nbr.isdigit():
        nbr = input("Combien de joueur êtes vous? ")
    nbr = int(nbr)
    list_joueur = []
    x = ["nom", "", 0]
    for i in range(nbr):
        y = deepcopy(x)
        list_joueur.append(y)
        list_joueur[i][0] = input(f"Quel est le nom du joueur n°{i + 1} ? ")
    return list_joueur


def affichage_plateau(plateau):
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


def utilise_lettre_plateau(coup, plateau):
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


def mots_perpendiculaires(coup, plateau, dico):
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
        - dico (list) : une liste dont chaque élément d'indice i, est un set de mots du dictionnaire de longueur (i+1).
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
    mot, pos, direc = coup
    line, column = pos
    a, b = pos
    d = 0
    nv_mot = ""
    liste_mots_perpendiculaire = []
    lettre_deja_presente = localisation_lettre_sur_plateau(coup, plateau)
    plateau_test = deepcopy(plateau)
    plateau_test = mot_sur_plateau(coup, plateau_test)
    if direc == "V":
        for i in range(len(mot)):
            for x in range(len(lettre_deja_presente)):
                if (line + i, column) == lettre_deja_presente[x]:
                    d += 1
            while plateau_test[a + i][b] != "_" and b > 0 and d == 0:
                b -= 1
            b += 1
            while plateau_test[a + i][b] != "_" and b < 14 and d == 0:
                nv_mot += plateau_test[a + i][b]
                b += 1
            if len(nv_mot) > 1:
                liste_mots_perpendiculaire.append(nv_mot)
            nv_mot = ""
            a, b = pos
            d = 0
    elif direc == "H":
        for i in range(len(mot)):
            for x in range(len(lettre_deja_presente)):
                if (line, column + i) == lettre_deja_presente[x]:
                    d += 1
            while plateau_test[a][b + i] != "_" and a > 0 and d == 0:
                a -= 1
            a += 1
            while plateau_test[a][b + i] != "_" and a < 14 and d == 0:
                nv_mot += plateau_test[a][b + i]
                a += 1
            if len(nv_mot) > 1:
                liste_mots_perpendiculaire.append(nv_mot)
            nv_mot = ""
            a, b = pos
    liste_mots_perpendiculaire.append(mot)
    if len(liste_mots_perpendiculaire) > 1:
        for test in liste_mots_perpendiculaire:
            if not verif_mot(test, dico):
                liste_mots_perpendiculaire = []
    liste_mots_perpendiculaire.sort()
    return liste_mots_perpendiculaire


def localisation_lettre_sur_plateau(coup, plateau):
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

    Valeur de retour:
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


def fifty_points(mot, lettre_en_plus):
    """
    Cette fonction renvoie un entier valant 50 si toutes les lettre du chevalet sont utilisées en un coup. Elle renvoie
    un entier valant 0 si ce n'est pas le cas.

    Args :
        mot (str) : chaine de caractère correspondant au mot que le joueur à placé.
        lettre_en_plus (str) : chaine de caractère correspondant au lettre déjà présente sur le plateau à l'emplacement
        du mot que le joueur veux jouer.

    Valeur de retour :
        - points (int) : entier valant 50 si toutes les lettre du chevalet sont utilisées en un coup, 0 dans le cas
        contraire

    Examples:
        >>> mot = "BONJOUR"
        >>> lettre_ en_plus = ""
        >>> fifty_points(mot, lettre_en_plus)
        50
    """
    x = len(lettre_en_plus)
    if len(lettre_en_plus) is None:
        x = 0
    if len(mot) > x + 6:
        points = 50
        print("Scrabble !")
    else:
        points = 0
    return points


def main():
    """
    Cette fonction ne sert qu'à faire tourner tout le jeu

    Args:
        /
    Valeur de retour:
        /
    """
    list_joueur = multijoueur()
    tour = 1
    dimensions = (15, 15)
    plateau_de_jeu = init_plateau(dimensions)
    dico_occu, dico_points = load_fichier_lettres("resources/Lettres.txt")
    dico_mot = list_dico("resources/dico.txt")
    pioche = init_pioche(dico_occu)
    while len(pioche) > 0:
        for i in range(len(list_joueur)):
            affichage_plateau(plateau_de_jeu)
            pioche, list_joueur[i][1] = jeton_joueur(pioche, list_joueur[i][1])
            print("C'est au tour de", list_joueur[i][0])
            print("Vous avez dans votre main les jetons suivants:", list_joueur[i][1])
            mot, pos, direc = propose_mot()
            while not mot_accepte(
                plateau_de_jeu,
                list_joueur[i][1],
                (mot, pos, direc),
                dico_mot,
                tour,
                dimensions,
            ):
                mot, pos, direc = propose_mot()
            lettre_en_plus = placer_mot((mot, pos, direc), plateau_de_jeu)
            pts_scrabble_fifty = fifty_points(mot, lettre_en_plus)
            list_joueur[i][2] = (
                list_joueur[i][2]
                + compte_points(
                    mots_perpendiculaires((mot, pos, direc), plateau_de_jeu, dico_mot),
                    dico_points,
                )
                + pts_scrabble_fifty
            )
            print(
                "Tu viens de marquer",
                compte_points(
                    mots_perpendiculaires((mot, pos, direc), plateau_de_jeu, dico_mot),
                    dico_points,
                )
                + pts_scrabble_fifty,
                "points.",
            )
            print("Tu as au total", list_joueur[i][2], "points.")
            list_joueur[i][1] = retirer_chevalet(list_joueur[i][1], mot, lettre_en_plus)
            plateau_de_jeu = mot_sur_plateau((mot, pos, direc), plateau_de_jeu)
            tour += 1


if __name__ == "__main__":
    main()
