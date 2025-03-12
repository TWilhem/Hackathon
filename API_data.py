import requests
import csv
import os
from datetime import datetime, timedelta

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

# Nom du fichier CSV
csv_file = 'meteo_valras_horaire.csv'

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

try:
    # Effectuer la requête à l'API
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    
    # Convertir la réponse en JSON
    data = response.json()
    
    # Récupérer l'heure actuelle
    now = datetime.now()
    current_hour = now.hour
    
    # Trouver l'index de l'heure actuelle dans les données
    current_hour_index = None
    for i, time_str in enumerate(data["hourly"]["time"]):
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
        if dt.hour == current_hour and dt.day == now.day and dt.month == now.month and dt.year == now.year:
            current_hour_index = i
            break
    
    if current_hour_index is not None:
        # Récupérer les données météo pour l'heure actuelle
        temp = data["hourly"]["temperature_2m"][current_hour_index]
        apparent_temp = data["hourly"]["apparent_temperature"][current_hour_index]
        precip = data["hourly"]["precipitation"][current_hour_index]
        wind_speed = data["hourly"]["windspeed_10m"][current_hour_index]
        wind_gusts = data["hourly"]["windgusts_10m"][current_hour_index]
        wind_direction = data["hourly"]["winddirection_10m"][current_hour_index]
        weather_code = data["hourly"]["weathercode"][current_hour_index]
        
        # Déterminer la direction du vent en texte
        wind_direction_text = ""
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
        else:
            wind_direction_text = "N"
        
        # Obtenir la description météo
        weather_description = weather_codes.get(weather_code, "Conditions inconnues")
        
        # Formater la date et l'heure
        timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
        
        # Préparer les données à écrire
        row_data = {
            "timestamp": timestamp,
            "temperature": temp,
            "ressenti": apparent_temp,
            "precipitation": precip,
            "vent_kmh": wind_speed,
            "rafales_kmh": wind_gusts,
            "direction_vent": wind_direction_text,
            "conditions": weather_description
        }
        
        # Vérifier si le fichier existe
        file_exists = os.path.isfile(csv_file)
        
        # Ouvrir le fichier en mode append
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            # Définir les en-têtes
            fieldnames = ["timestamp", "temperature", "ressenti", "precipitation", 
                         "vent_kmh", "rafales_kmh", "direction_vent", "conditions"]
            
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            # Écrire les en-têtes si le fichier n'existe pas
            if not file_exists:
                writer.writeheader()
            
            # Écrire la ligne de données
            writer.writerow(row_data)
        
        print(f"Données météo de {timestamp} enregistrées dans '{csv_file}'")
        
    else:
        print("Impossible de trouver l'heure actuelle dans les données de prévision.")
        
except requests.exceptions.RequestException as err:
    print(f"Erreur lors de la requête: {err}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()