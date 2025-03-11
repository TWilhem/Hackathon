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
    
    # Fonction pour nettoyer le texte
    def clean_text(text):
        if not text:
            return None
        return ' '.join(text.strip().split())
    
    # Fonction pour extraire les informations météo à partir d'une section de période
    def extract_weather_info(period_class, period_name):
        info = {'période': period_name}
        
        # Trouver le h4 avec la classe spécifique de la période
        h4_element = soup.find('h4', class_=period_class)
        if not h4_element:
            return info
            
        # Trouver la section parent qui contient toutes les données
        section = h4_element
        for _ in range(5):  # Essayer de remonter jusqu'à 5 niveaux
            section = section.parent
            
            # Chercher les éléments de météo dans cette section
            temp_elem = section.find(class_=lambda c: c and ('temperature' in c or 'temp' in c))
            if temp_elem:
                temp_text = clean_text(temp_elem.text)
                if temp_text:
                    # Extraire la température principale
                    if '°' in temp_text:
                        parts = temp_text.split('°', 1)
                        info['température'] = parts[0] + '°'
                        
                        # Extraire le ressenti s'il est dans le même élément
                        if 'Ressenti' in parts[1]:
                            ressenti_parts = parts[1].split('Ressenti', 1)[1].strip()
                            if '°' in ressenti_parts:
                                info['ressenti'] = ressenti_parts.split('°')[0].strip() + '°'
            
            # Si ressenti n'a pas été trouvé dans le texte de température
            if 'ressenti' not in info:
                ressenti_elem = section.find(text=lambda t: t and 'Ressenti' in t)
                if ressenti_elem:
                    ressenti_text = clean_text(ressenti_elem)
                    if ressenti_text and '°' in ressenti_text:
                        info['ressenti'] = ressenti_text.split('°')[0].replace('Ressenti', '').strip() + '°'
            
            # Chercher le vent
            vent_elem = section.find(class_=lambda c: c and ('vent' in c or 'wind' in c))
            if vent_elem:
                vent_text = clean_text(vent_elem.text)
                if vent_text:
                    info['vent'] = vent_text
                    
                    # Séparer les rafales et la direction si possible
                    if 'Rafales' in vent_text and 'km/h' in vent_text:
                        parts = vent_text.split('Rafales', 1)
                        rafales = 'Rafales' + parts[1].split('km/h')[0].strip() + 'km/h'
                        
                        # La direction est généralement après les rafales
                        if len(parts[1].split('km/h')) > 1:
                            direction = parts[1].split('km/h')[1].strip()
                            info['rafales'] = rafales
                            info['direction_vent'] = direction
            
            # Chercher les conditions/résumé
            conditions_elem = section.find(class_=lambda c: c and ('resume' in c or 'summary' in c or 'weather-description' in c))
            if conditions_elem:
                conditions_text = clean_text(conditions_elem.text)
                if conditions_text:
                    info['conditions'] = conditions_text
            
            # Chercher les précipitations
            pluie_elem = section.find(class_=lambda c: c and ('pluie' in c or 'rain' in c or 'precipitation' in c))
            if pluie_elem:
                pluie_text = clean_text(pluie_elem.text)
                if pluie_text:
                    info['précipitations'] = pluie_text
            
            # Si on a trouvé au moins une info météo, on s'arrête
            if len(info) > 1:
                break
                
        return info
    
    # Définir les périodes et leurs classes correspondantes
    periods = [
        {'name': 'De 9h à 12h', 'class': 'quarter-type-morning'},
        {'name': 'Cet après-midi', 'class': 'quarter-type-afternoon'},
        {'name': 'Ce soir', 'class': 'quarter-type-evening'},
        {'name': 'Nuit', 'class': 'quarter-type-night'}
    ]
    
    # Extraire les informations pour chaque période
    weather_data = [extract_weather_info(p['class'], p['name']) for p in periods]
    
    # Convertir les données en JSON
    weather_json = json.dumps(weather_data, ensure_ascii=False, indent=4)
    print(weather_json)
    
except requests.exceptions.RequestException as err:
    print(f"Erreur lors de la requête: {err}")
except Exception as e:
    print(f"Erreur inattendue: {e}")