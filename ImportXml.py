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

# Listes à exclure
excluded_tags = {"DESIGC","DESIGR","GESTION"}

def xml_to_dict(element):
    """Convertit un élément XML en dictionnaire en gérant les balises répétées tout en excluant certaines listes."""
    result = {}
    
    for child in element:
        if child.tag in excluded_tags:
            continue  # Ignorer les balises exclues
        
        child_data = xml_to_dict(child) if len(child) else child.text.strip() if child.text else None
        
        if child.tag in result:
            # Si la clé existe déjà, transformer en liste si ce n'est pas déjà une liste
            if not isinstance(result[child.tag], list):
                result[child.tag] = [result[child.tag]]
            result[child.tag].append(child_data)
        else:
            result[child.tag] = child_data

    return result

# Convertir le XML en dictionnaire
data_dict = xml_to_dict(root)

# Convertir en JSON
json_data = json.dumps(data_dict, indent=4, ensure_ascii=False)

# Sauvegarder le JSON
json_file = "FR9101434.json"
with open(json_file, "w", encoding="utf-8") as f:
    f.write(json_data)

print(f"Données converties et sauvegardées dans {json_file}")