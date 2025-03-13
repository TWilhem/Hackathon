import os
import requests
import json
from datetime import datetime

def get_species_image(species_name, save_folder="images"):
    headers = {"User-Agent": "MyScientificBot/1.0 (https://example.com/contact)"}
    url = "https://fr.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": species_name,
        "prop": "pageimages",
        "pithumbsize": 500
    }
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_info in pages.items():
        if "thumbnail" in page_info:
            image_url = page_info["thumbnail"]["source"]
            img_response = requests.get(image_url, headers=headers, stream=True)
            if "text/html" in img_response.headers.get("Content-Type", ""):
                return f"Erreur : Wikimedia refuse l'accès à l'image pour {species_name}."
            
            os.makedirs(save_folder, exist_ok=True)
            image_name = species_name.replace(" ", "_") + ".jpg"
            image_path = f"../image/{image_name}"
            
            with open(image_path, "wb") as file:
                for chunk in img_response.iter_content(1024):
                    file.write(chunk)
            
            return f"Image enregistrée : {image_path}"
    
    return f"Aucune image trouvée pour {species_name}."

Month = datetime.now().strftime("%m")
Year = datetime.now().strftime("%Y")

# Chargement des données JSON
with open(f"../Archive/Info_Espece_{Month}_{Year}.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extraction des espèces
species_list = [species["LB_NOM"] for species in data["SPECIES_OTHER"]["SPECIES_OTHER_ROW"]]

# Téléchargement des images pour chaque espèce
for species in species_list:
    result = get_species_image(species)
    print(result)