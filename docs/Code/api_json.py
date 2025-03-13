import requests
import json
import os
from datetime import datetime

# URL de base de l'API Open-Meteo
base_url = "https://api.open-meteo.com/v1/forecast"

# Coordonnées de Valras-Plage (Les Orpellieres)
latitude = 43.2504
longitude = 3.2926

# Les paramètres de la requête - on récupère uniquement l'heure actuelle
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,apparent_temperature,precipitation,weathercode,windspeed_10m,winddirection_10m,windgusts_10m",
    "timezone": "Europe/Paris",
    "forecast_days": 1  # Limiter aux prévisions du jour actuel
}

# Nom du fichier JSON
json_file = 'meteo_valras_hebdo.json'
chemin = f'../Archive/{json_file}'

# Nombre maximum d'entrées conservées
MAX_ENTRIES = 336

def fetch_weather_data():
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Récupérer l'heure actuelle
        now = datetime.now()
        current_hour = now.hour
        
        # Trouver l'index de l'heure actuelle dans les données
        current_hour_index = None
        for i, time_str in enumerate(data["hourly"]["time"]):
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            if dt.hour == current_hour and dt.date() == now.date():
                current_hour_index = i
                break
        
        if current_hour_index is not None:
            new_entry = {
                "timestamp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "temperature": data["hourly"]["temperature_2m"][current_hour_index],
                "ressenti": data["hourly"]["apparent_temperature"][current_hour_index],
                "precipitation": data["hourly"]["precipitation"][current_hour_index],
                "vent_kmh": data["hourly"]["windspeed_10m"][current_hour_index],
                "rafales_kmh": data["hourly"]["windgusts_10m"][current_hour_index],
                "direction_vent": data["hourly"]["winddirection_10m"][current_hour_index],
                "conditions": data["hourly"]["weathercode"][current_hour_index]
            }
            
            # Charger les entrées existantes
            entries = []
            if os.path.isfile(chemin):
                try:
                    with open(chemin, 'r', encoding='utf-8') as f:
                        entries = json.load(f)
                    if not isinstance(entries, list):
                        entries = []
                except Exception as e:
                    print(f"Erreur lecture JSON: {e}, création d'un nouveau fichier...")
            
            # Ajouter la nouvelle entrée
            entries.append(new_entry)
            
            # Supprimer les entrées les plus anciennes si la limite est dépassée
            if len(entries) > MAX_ENTRIES:
                entries.pop(0)
            
            # Sauvegarder les entrées mises à jour
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            
            print(f"Données météo enregistrées. Nombre d'entrées: {len(entries)}")
        else:
            print("Aucune donnée météo trouvée pour l'heure actuelle.")
    
    except requests.exceptions.RequestException as err:
        print(f"Erreur requête API: {err}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")


fetch_weather_data()

