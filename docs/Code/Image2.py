import json
import requests
import os
from PIL import Image
from io import BytesIO
from datetime import datetime

# Remplacez ceci par votre clé API Unsplash
access_key = 'H-7lB7zDdgkXveEX6uaNG9px4UQ4D1mTF-NR_FRE3fU'

# Définir le dossier de sauvegarde des images
output_dir = "images_species"
os.makedirs(output_dir, exist_ok=True)

def get_image_from_unsplash(query):
    url = f"https://api.unsplash.com/photos/random?query={query}&client_id={access_key}&count=1"
    response = requests.get(url)
    
    if response.status_code == 200 and response.json():
        return response.json()[0]['urls']['regular']
    else:
        print(f"Aucune image trouvée pour {query}")
        return None

def save_image(image_url, file_name):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    file_path = f"../image/{file_name}"
    img.save(file_path)
    print(f"Image sauvegardée dans : {file_path}")

def process_species_from_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Récupérer les espèces dans SPECIES_OTHER
    species_list = data.get("SPECIES_OTHER", {}).get("SPECIES_OTHER_ROW", [])
    
    for species in species_list:
        name = species.get("LB_NOM")
        if name:
            print(f"Recherche d'image pour : {name}")
            image_url = get_image_from_unsplash(name)
            
            if image_url:
                file_name = name.replace(" ", "_") + ".jpg"
                save_image(image_url, file_name)

if __name__ == "__main__":
    Month = datetime.now().strftime("%m")
    Year = datetime.now().strftime("%Y")
    json_file_path = f"../Archive/Info_Espece_{Month}_{Year}.json"  # Remplacez par le chemin réel de votre fichier JSON
    process_species_from_json(json_file_path)
