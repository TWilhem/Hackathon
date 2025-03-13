import requests
import json
import os
from datetime import datetime

# URL de base de l'API Open-Meteo
base_url = "https://api.open-meteo.com/v1/forecast"

# Coordonnées de Valras-Plage (Les Orpellieres)
latitude = 43.2504
longitude = 3.2926

# Paramètres de la requête
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,apparent_temperature,precipitation,weathercode,windspeed_10m,winddirection_10m,windgusts_10m",
    "timezone": "Europe/Paris",
    "forecast_days": 1
}

# Fichier JSON
json_file = 'meteo_valras_hebdo.json'
chemin = f'../Archive/{json_file}'
MAX_ENTRIES = 336

# Conversion des codes météo en descriptions
weather_codes = {
    0: "Ciel dégagé",
    1: "Principalement dégagé",
    2: "Partiellement nuageux",
    3: "Nuageux",
    45: "Brouillard",
    48: "Brouillard givrant",
    51: "Bruine légère",
    53: "Bruine modérée",
    55: "Bruine dense",
    56: "Bruine verglaçante légère",
    57: "Bruine verglaçante dense",
    61: "Pluie légère",
    63: "Pluie modérée",
    65: "Pluie forte",
    66: "Pluie verglaçante légère",
    67: "Pluie verglaçante forte",
    71: "Neige légère",
    73: "Neige modérée",
    75: "Neige forte",
    77: "Grains de neige",
    80: "Averses de pluie légères",
    81: "Averses de pluie modérées",
    82: "Averses de pluie violentes",
    85: "Averses de neige légères",
    86: "Averses de neige fortes",
    95: "Orage",
    96: "Orage avec grêle légère",
    99: "Orage avec grêle forte"
}

# Fonction de récupération des données météo
def fetch_weather_data():
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()
        
        now = datetime.now()
        current_hour = now.hour
        
        # Trouver l'index de l'heure actuelle
        current_hour_index = next(
            (i for i, time_str in enumerate(data["hourly"]["time"])
             if datetime.fromisoformat(time_str.replace("Z", "+00:00")).hour == current_hour),
            None
        )
        
        if current_hour_index is not None:
            wind_direction = data["hourly"]["winddirection_10m"][current_hour_index]
            wind_direction_text = "N"  # Par défaut
            if 22.5 <= wind_direction < 67.5:
                wind_direction_text = "NE"
            elif 67.5 <= wind_direction < 112.5:
                wind_direction_text = "E"
            elif 112.5 <= wind_direction < 157.5:
                wind_direction_text = "SE"
            elif 157.5 <= wind_direction < 202.5:
                wind_direction_text = "S"
            elif 202.5 <= wind_direction < 247.5:
                wind_direction_text = "SO"
            elif 247.5 <= wind_direction < 292.5:
                wind_direction_text = "O"
            elif 292.5 <= wind_direction < 337.5:
                wind_direction_text = "NO"
                
            new_entry = {
                "temp": now.strftime("%Y-%m-%d %H:%M:%S"),
                "apparent_temp": data["hourly"]["temperature_2m"][current_hour_index],
                "precip": data["hourly"]["apparent_temperature"][current_hour_index],
                "precipitation": data["hourly"]["precipitation"][current_hour_index],
                "wind_speed": data["hourly"]["windspeed_10m"][current_hour_index],
                "wind_gusts": data["hourly"]["windgusts_10m"][current_hour_index],
                "wind_direction": wind_direction_text,
                "weather_code": weather_codes.get(data["hourly"]["weathercode"][current_hour_index], "Conditions inconnues")
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
            
            # Ajouter la nouvelle entrée et limiter le nombre d'entrées
            entries.append(new_entry)
            if len(entries) > MAX_ENTRIES:
                entries.pop(0)
            
            # Sauvegarder les données mises à jour
            with open(chemin, 'w', encoding='utf-8') as f:
                json.dump(entries, f, ensure_ascii=False, indent=2)
            
            print(f"Données météo enregistrées: {chemin}")
        else:
            print("Aucune donnée météo trouvée pour l'heure actuelle.")
    except requests.exceptions.RequestException as err:
        print(f"Erreur requête API: {err}")
    except Exception as e:
        print(f"Erreur inattendue: {e}")


fetch_weather_data()

