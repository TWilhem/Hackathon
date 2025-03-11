import requests
from bs4 import BeautifulSoup
import json

# URL de la page à scraper
url = 'https://www.lachainemeteo.com/meteo-france/plage-1814/previsions-meteo-valras-plage-plage-les-orpellieres-aujourdhui#beach-infos'

try:
    # Ajouter un user-agent pour éviter d'être bloqué
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    # Parser le contenu HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Fonction pour extraire les informations météo à partir d'une section de période
    def extract_weather_info(period_class):
        info = {}
        
        # Trouver le h4 avec la classe spécifique de la période
        h4_element = soup.find('h4', class_=period_class)
        if not h4_element:
            return info
            
        # Obtenir le texte de la période
        info['période'] = h4_element.text.strip()
        
        # Trouver la section parent qui contient toutes les données
        # Il faut remonter plusieurs niveaux pour atteindre le conteneur principal
        section = h4_element
        for _ in range(5):  # Essayer de remonter jusqu'à 5 niveaux au maximum
            section = section.parent
            
            # Chercher les éléments de météo dans cette section
            temp_elem = section.find(class_=lambda c: c and ('temperature' in c or 'temp' in c))
            if temp_elem:
                info['température'] = temp_elem.text.strip()
                
            ressenti_elem = section.find(class_=lambda c: c and 'ressenti' in c)
            if ressenti_elem:
                info['ressenti'] = ressenti_elem.text.strip()
                
            vent_elem = section.find(class_=lambda c: c and ('vent' in c or 'wind' in c))
            if vent_elem:
                info['vent'] = vent_elem.text.strip()
                
            conditions_elem = section.find(class_=lambda c: c and ('resume' in c or 'summary' in c or 'weather-description' in c))
            if conditions_elem:
                info['conditions'] = conditions_elem.text.strip()
                
            pluie_elem = section.find(class_=lambda c: c and ('pluie' in c or 'rain' in c or 'precipitation' in c))
            if pluie_elem:
                info['précipitations'] = pluie_elem.text.strip()
            
            # Si on a trouvé au moins une info météo, on s'arrête
            if len(info) > 1:  # Plus que juste la période
                break
                
        return info
    
    # Extraire les informations pour chaque période
    weather_data = [
        extract_weather_info('quarter-type-morning'),    # De 9h à 12h
        extract_weather_info('quarter-type-afternoon'),  # Cet après-midi
        extract_weather_info('quarter-type-evening'),    # Ce soir
        extract_weather_info('quarter-type-night')       # Nuit
    ]
    
    # Ajouter une étape d'inspection détaillée
    for i, period_data in enumerate(weather_data):
        if len(period_data) <= 1:  # Si on n'a pas trouvé de données météo
            period_class = ['quarter-type-morning', 'quarter-type-afternoon', 'quarter-type-evening', 'quarter-type-night'][i]
            h4_element = soup.find('h4', class_=period_class)
            if h4_element:
                # Trouver le parent le plus pertinent
                parent = h4_element.parent
                print(f"\nEléments trouvés pour {period_data.get('période', 'période inconnue')}:")
                
                # Explorer et imprimer tous les éléments qui pourraient contenir des données météo
                for element in parent.find_all(['div', 'span', 'p']):
                    if element.get('class'):
                        print(f"Élément {element.name} avec classe {element.get('class')}: {element.text.strip()}")
                    elif element.text.strip():
                        print(f"Élément {element.name} sans classe: {element.text.strip()}")
    
    # Convertir les données en JSON
    weather_json = json.dumps(weather_data, ensure_ascii=False, indent=4)
    print("\nDonnées météo extraites:")
    print(weather_json)
    
except requests.exceptions.RequestException as err:
    print(f"Erreur lors de la requête: {err}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()