import pandas as pd
import urllib
import json
import re

# WIKIPEDIA DICTIONARY ---------------------


def dictionnary_from_wiki_category(
    categorie=None,
    n: int = 10,
    filters="Utilisateur|Discussion|Classement|Liste|Catégorie",
    sub="\(.*\)",
):
    """
    Scrap wikipedia categories
    Parameters
    ----------
    categorie: Wikipedia categories to scrap. Default to ['Bière blonde', 'Vin_français', 'Marque de bière']
    n: Number of child page scrapped
    filters: Possibility to apply a filter for some topics
    sub: Regular expression to replace some pattern
    Returns
    -------
    """

    if categorie is None:
        categorie = ["Bière blonde", "Vin_français", "Marque de bière"]
    if isinstance(categorie, list):
        categorie = categorie[0]

    url = (
        "https://fr.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:"
        + urllib.parse.quote(categorie)
        + "&cmlimit="
        + str(n)
        + "&format=json"
    )

    with urllib.request.urlopen(url) as response:
        jsonresp = response.read()

    jsonresp = json.loads(jsonresp)["query"]["categorymembers"]

    if len(jsonresp) > 1:
        res = [
            re.sub(sub, "", x["title"]).strip()
            for x in jsonresp
            if not re.match(filters, x["title"])
        ]
        return res
    else:
        return []


def dictionnary_from_wiki_categories(
    CAT=None, filters="Utilisateur|Modèle|Discussion|Classement|Liste|Catégorie"
):
    """
    Scrap wikipedia and return as dictionary
    Parameters
    ----------
    CAT: Categories that should be scrapped
    filters: Filter to exclude some topics
    Returns
    -------
    A dictionary
    """

    if CAT is None:
        CAT = ["Bière blonde", "Marque de bière"]

    ITEMS = []

    for b in CAT:
        ITEMS = ITEMS + dictionnary_from_wiki_category(b, 1000, filters)

    return list(set(ITEMS))


def dictionnary_by_descending_wiki_child_categories(CAT=None, max_step=6):
    """
    Create a dictionary from network of page results
    Parameters
    ----------
    CAT: Categories that should be scrapped
    max_step: Number of child page scrapped
    Returns
    -------
    """

    # Sur l'exemple du vin :)
    if CAT is None:
        CAT = ["Vin_français", "Vin AOC en France par région"]

    VINS_ITEM = []
    VINS_CAT = CAT
    VINS_CAT_DONE = []
    i = 0

    while len(VINS_CAT) > 0 and (i < max_step):
        print("--- Catégories à traiter --- ")
        print(VINS_CAT)
        VINS_CAT_DONE = VINS_CAT_DONE + VINS_CAT
        VINS = dictionnary_from_wiki_categories(
            VINS_CAT, filters="Utilisateur|Discussion|Classement|Liste"
        )
        VINS_CAT = [
            re.sub("Catégorie:", "", cat)
            for cat in VINS
            if (re.match("Catégorie:", cat))
            and not (re.sub("Catégorie:", "", cat) in VINS_CAT_DONE)
        ]  # Evite de rechercher une catégorie déjà explorée.
        VINS_ITEM = VINS_ITEM + [vin for vin in VINS if not re.match("Catégorie:", vin)]
        i += 1
        print(i)

    out = {"items": VINS_ITEM, "scrawl_cat": VINS_CAT_DONE}
    return out
