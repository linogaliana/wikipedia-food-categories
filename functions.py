import urllib
import json
import re
import pandas as pd

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


Wiki_to_ciqual = {
    'BIERES_BLANCHES': {
        'ciqual' : 'Bière blanche',
        'wiki': ['Bière blanche']
    },
    'BIERES_BRUNES':  {
        'ciqual' : 'Bière blanche',
        'wiki': ['Bière brune']
    },
    'BIERES_AUTRES': {
        'ciqual' : 'Bière blanche',
        'wiki': ['Bière blonde','Marque de bière'],
        'max_child': 3
    },
    'VINS':  {
        'ciqual' : 'Vin rouge',
        'wiki':  ['Vin AOC en France par région','Vin_français']
    },
    'FROMAGES': {
        'ciqual': 'Fromage (aliment moyen)',
        'wiki': ['Marque_de_fromage_en_France','Fromage_français']
    },
    'CHARCUTERIE': {
        'ciqual' : 'Charcuterie (aliment moyen)',
        'wiki': ['Charcuterie'],
        'max_child': 2
    },
    'CHIPS': {
        'ciqual' : 'Chips de pommes de terre nature ou aromatisées, standard',
        'wiki': ['Marque_de_chips']
    }, 
    'CAFES':  {
        'ciqual' : 'Café, moulu',
        'wiki': ['Marque de café']
    },
    'VIANDES': {
        'ciqual' :  'Viande cuite (aliment moyen)',
        'wiki': ['Découpe de viande','Grillade','Viande bovine']
    },
    'LIQUEUR' :  {
        'ciqual' : 'Liqueur',
        'wiki': ['Marque de liqueur']
    },
    'COGNAC': {
        'ciqual': 'Eau de vie de vin, type armagnac, cognac',
        'wiki': ['Marque de cognac']
    },
      'RHUM': {
        'ciqual': 'Rhum',
        'wiki': ['Marque de rhum']
    },
    'VERMOUTH':{
        'ciqual': 'Liqueur',
        'wiki':[ 'Marque de vermouth']
    },
    'WHISKY':{
        'ciqual': 'Whisky',
        'wiki':[ 'Marque de whisky']
    },
    'VODKA': {
        'ciqual': 'Vodka',
        'wiki': ['Marque de vodka']
    }
}


def create_dataframe_wikipedia(Wiki_to_ciqual):
    wiki_products = pd.DataFrame(columns = ['LIBELLE','alim_nom_fr'])

    for d in Wiki_to_ciqual.keys():
        #print('____Loading From Wikipedia the following categories ____')
        #print(Wiki_to_ciqual[d])
        max_step = 10
        if 'max_child' in Wiki_to_ciqual[d].keys():
            max_step = Wiki_to_ciqual[d]['max_child']
        items = dictionnary_by_descending_wiki_child_categories(Wiki_to_ciqual[d]['wiki'], max_step = max_step)
        
        #print('-> Liste des produits wikipédia ajouté à Ciqual:')
        #print(items)
        #print('_________________________________________________________')
        
        items = pd.DataFrame({'LIBELLE':  [re.sub('-',' ',x) for x in items['items']], 'alim_nom_fr': Wiki_to_ciqual[d]['ciqual']})
        #items = cleanlibel.clean_labels(items, yvar = 'LIBELLE', outvar = 'libel_clean_wiki')
        wiki_products = pd.concat([wiki_products, items])

        
    # --- filter products with double meaning

    # --- Add short-cut for common products which have long descriptive names in ciqual - which does not favor matching.
    items = pd.DataFrame({'LIBELLE':  ['Citron','Mangue','Orange','Coca-cola','Fraise','Cerise','Yaourt','Pizza','Pizza chorizo','Kiwi','Pommes de terre','Ananas','Tomate cerise','Muffin','Bière'], 
                        'alim_nom_fr': ['Citron vert ou Lime, pulpe, cru','Orange, pulpe, crue','Mangue, pulpe, crue','Cola, teneur en sucre et édulcorant inconnue (aliment moyen)','Fraise, crue','Cerise, dénoyautée, crue','Yaourt ou spécialité laitière nature ou aux fruits (aliment moyen)','Pizza (aliment moyen)','Pizza (aliment moyen)','Kiwi, pulpe et graines, cru','Pomme de terre, sans peau, rôtie/cuite au four','Ananas Victoria ou ananas Queen Victoria, pulpe crue, prélevé à La Réunion Ananas comosus (L.) merr var. Queen)','Tomate cerise, crue','Muffin anglais, complet, petit pain spécial, préemballé','Bière blanche']})

    #print('_________ Short-cut for common products which have long descriptive names in ciqual ____ ')
    #print(items)
    wiki_products = pd.concat([wiki_products, items])
    return wiki_products