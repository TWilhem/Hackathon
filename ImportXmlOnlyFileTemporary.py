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
    "HABIT1", "HABIT1_ROW", "LB_HABDH_FR", "REPRESENT", "REL_SURF", "CONSERVE", "GLOBAL", "QUALITY",
    "HABIT2", "HABIT2_ROW", "DESCRIPTFR", "COVER",
    "SPECIES_OTHER", "SPECIES_OTHER_ROW", "TAXGROUP", "SIZE_MAX", "UNIT", "CAT_POP", "CAT_MOTIV", "A", "B", "C", "D", "LB_NOM"
}

def xml_to_dict(element, allowed_tags):
    """Convertit un élément XML en dictionnaire en conservant uniquement certaines balises."""
    result = {}
    
    for child in element:
        if child.tag not in allowed_tags:
            continue  # Ignorer les balises non incluses
        
        child_data = xml_to_dict(child, allowed_tags) if len(child) else child.text.strip() if child.text else None
        
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

# Recuperation Time
Month = datetime.now().strftime("%m")
Year = datetime.now().strftime("%Y")

# Sauvegarder les fichiers JSON
json_file_part2 = f"Info_Espece_{Month}_{Year}.json"

with open(json_file_part2, "w", encoding="utf-8") as f:
    f.write(json_data_part2)

print(f"Données converties et sauvegardées dans {json_file_part2}")