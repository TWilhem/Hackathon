import xml.etree.ElementTree as ET
import json
import requests

# URL du fichier XML
xml_url = "https://inpn.mnhn.fr/docs/natura2000/fsdxml/FR9101434.xml"

# Télécharger le fichier XML
response = requests.get(xml_url)
xml_content = response.content

# Parser le contenu XML
root = ET.fromstring(xml_content)

# Balises pour le premier fichier
first_part_tags = {
    "DATE_EDIT", "REG", "SITE_NAME", "LONGITUDE", "LATITUDE", 
    "MANAGER", "MANAGER_ROW", "NAME", "ADDRESS", "POST_CODE", 
    "RESPONDENT", "REPONDENT_ROW", "EMAIL", "POST_NAME", "PHONE", 
    "OWNERSHIP", "OWNERSHIP_ROW", "LB_STPRO", "DATE_CREA", "DATE_BASE",
    "COMMUNES", "COMMUNES_ROW", "LB_ADM"
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
data_dict_part1 = xml_to_dict(root, first_part_tags)

# Convertir en JSON
json_data_part1 = json.dumps(data_dict_part1, indent=4, ensure_ascii=False)

# Sauvegarder les fichiers JSON
json_file_part1 = "Info_Admin.json"

with open(json_file_part1, "w", encoding="utf-8") as f:
    f.write(json_data_part1)

print(f"Données converties et sauvegardées dans {json_file_part1}")