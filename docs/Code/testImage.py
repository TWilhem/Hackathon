import requests
from bs4 import BeautifulSoup

def get_wikipedia_infobox_image(nom_scientifique):
    # Transformer le nom scientifique pour l'URL Wikipédia
    nom_page = nom_scientifique.replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{nom_page}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Erreur lors de la requête, statut {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Chercher l'infobox qui contient l'image principale
    infobox = soup.find("table", class_="infobox")
    if not infobox:
        print("Infobox non trouvée.")
        return None
    
    # Extraire la première image dans l'infobox
    img_tag = infobox.find("img")
    if not img_tag:
        print("Aucune image dans l'infobox.")
        return None
    
    img_url = img_tag.get("src")
    if img_url.startswith("//"):
        img_url = "https:" + img_url
    return img_url

def download_image(image_url, save_path):
    # Télécharger l'image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Écriture en mode binaire
        with open(save_path, "wb") as f:
            f.write(response.content)
        print("Image enregistrée dans", save_path)
    else:
        print("Erreur lors du téléchargement de l'image, statut:", response.status_code)

# Test avec un nom scientifique
nom_scientifique = "Panthera leo"  # Lion
image_url = get_wikipedia_infobox_image(nom_scientifique)

if image_url:
    print("Image trouvée:", image_url)
    # Spécifie le chemin et le nom du fichier à enregistrer
    save_path = "Panthera_leo.jpg"
    download_image(image_url, save_path)
else:
    print("Aucune image trouvée.")
