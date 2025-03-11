import xml.etree.ElementTree as ET
import json
import requests
from datetime import datetime

# URL du fichier XML
xml_url = "https://inpn.mnhn.fr/docs/natura2000/fsdxml/FR9101434.xml"

# Télécharger le fichier XML
response = requests.get(xml_url)
xml_content = response.content

# Parser le contenu XML
root = ET.fromstring(xml_content)

second_part_tags = {
    "HABIT1", "HABIT1_ROW", "LB_HABDH_FR", "PF", "QUALITY", "REPRESENT", "REL_SURF", "CONSERVE", "GLOBAL",
    "HABIT2", "HABIT2_ROW", "DESCRIPTFR", "COVER",
    "SPECIES_OTHER", "SPECIES_OTHER_ROW", "TAXGROUP", "SIZE_MAX", "UNIT", "CAT_POP", "CAT_MOTIV", "LB_NOM"
}

def get_PF_value(PF):
    if PF is None:
        return None
    return "Forme prioritaire de l'habitat" if "true" in PF else ""

def get_QUALITY_value(QUALITY):
    return {"G": "Bonne", "M": "Moyenne", "P": "Médiocre"}.get(QUALITY.upper(), "Non défini") if QUALITY else None

def get_REPRESENT_value(REPRESENT):
    return {"A": "Excellente", "B": "Bonne", "C": "Significative", "D": "Présence non significative"}.get(REPRESENT.upper(), "Non défini") if REPRESENT else None

def get_REL_SURF_value(REL_SURF):
    return {"A": "100% - 15%", "B": "15% - 2%", "C": "2% - 0%"}.get(REL_SURF.upper(), "Non défini") if REL_SURF else None

def get_CONSERVE_value(CONSERVE):
    return {"A": "Excellente", "B": "Bonne", "C": "Moyenne/réduite"}.get(CONSERVE.upper(), "Non défini") if CONSERVE else None

def get_GLOBAL_value(GLOBAL):
    return {"A": "Excellente", "B": "Bonne", "C": "Significative"}.get(GLOBAL.upper(), "Non défini") if GLOBAL else None

def get_TAXGROUP_value(TAXGROUP):
    return {"A": "Amphibiens", "B": "Oiseaux", "F": "Poissons", "Fu": "Champignons", "I": "Invertébrés", "L": "Lichens", "M": "Mammifères", "P": "Plantes", "R": "Reptiles"}.get(TAXGROUP, "Non défini") if TAXGROUP else None

def get_UNIT_value(UNIT):
    return {"i": "Individus", "p": "Couples", "adults": "Adultes matures", "area": "Superficie en m2", "bfemales": "Femelles reproductrices", "cmales": "Mâles chanteurs", "colonies": "Colonies", "fstems": "Tiges florales", "grids1x1": "Grille 1x1 km", "grids10x10": "Grille 10x10 km", "grids5x5": "Grille 5x5 km", "length": "Longueur en km", "localities": "Stations", "logs": "Nombre de branches", "males": "Mâles", "shoots": "Pousses", "stones": "Cavités rocheuses", "subadults": "Sub-adultes", "trees": "Nombre de troncs", "tufts": "Touffes"}.get(UNIT, "Non défini") if UNIT else None

def get_CAT_POP_value(CAT_POP):
    return {"C": "Espèce commune", "R": "Espèce rare", "V": "Espèce très rare", "P": "Espèce présente"}.get(CAT_POP, "Non défini") if CAT_POP else None

def get_CAT_MOTIV_value(CAT_MOTIV):
    if CAT_MOTIV:
        CAT_MOTIV = CAT_MOTIV.replace("-", "").replace("E", "")
    return {"A": "Liste rouge nationale", "B": "Espèce endémique", "C": "Conventions internationales", "D": "Autres raisons"}.get(CAT_MOTIV, "Non défini") if CAT_MOTIV else None

transform_functions = {
    "PF": get_PF_value,
    "QUALITY": get_QUALITY_value,
    "REPRESENT": get_REPRESENT_value,
    "REL_SURF": get_REL_SURF_value,
    "CONSERVE": get_CONSERVE_value,
    "GLOBAL": get_GLOBAL_value,
    "TAXGROUP": get_TAXGROUP_value,
    "UNIT": get_UNIT_value,
    "CAT_POP": get_CAT_POP_value,
    "CAT_MOTIV": get_CAT_MOTIV_value
}

def xml_to_dict(element, allowed_tags):
    """Convertit un élément XML en dictionnaire en appliquant les transformations aux balises spécifiques."""
    result = {}
    
    for child in element:
        if child.tag not in allowed_tags:
            continue  # Ignorer les balises non incluses
        
        child_data = xml_to_dict(child, allowed_tags) if len(child) else child.text.strip() if child.text else None
        
        # Appliquer la transformation si une fonction est définie pour cette balise
        if child.tag in transform_functions and child_data:
            child_data = transform_functions[child.tag](child_data)
        
        if child.tag in result:
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data

    return result

# Convertir les parties du XML en dictionnaire
data_dict_part2 = xml_to_dict(root, second_part_tags)

# Convertir en JSON
json_data_part2 = json.dumps(data_dict_part2, indent=4, ensure_ascii=False)

# Récupération du mois et de l'année
Month = datetime.now().strftime("%m")
Year = datetime.now().strftime("%Y")

# Sauvegarder les fichiers JSON
Chemin = "../Archive/"
json_file_part2 = f"Info_Espece_{Month}_{Year}.json"

with open(f"{Chemin}{json_file_part2}", "w", encoding="utf-8") as f:
    f.write(json_data_part2)

print(f"Données converties et sauvegardées dans {json_file_part2}")
