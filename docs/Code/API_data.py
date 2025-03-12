import requests
import json
from datetime import datetime

# URL de base de l'API Open-Meteo
base_url = "https://api.open-meteo.com/v1/forecast"

# Coordonnées de Valras-Plage (Les Orpellieres)
# Ces coordonnées peuvent être ajustées selon l'emplacement exact
latitude = 43.2504
longitude = 3.2926

# Les paramètres de la requête
params = {
    "latitude": latitude,
    "longitude": longitude,
    "hourly": "temperature_2m,apparent_temperature,precipitation,weathercode,windspeed_10m,winddirection_10m,windgusts_10m",
    "timezone": "Europe/Paris",
    "forecast_days": 1  # Limiter aux prévisions du jour actuel
}

try:
    # Effectuer la requête à l'API
    response = requests.get(base_url, params=params)
    response.raise_for_status()  # Lever une exception si la requête échoue
    
    # Convertir la réponse en JSON
    data = response.json()
    
    # Récupérer la date actuelle
    now = datetime.now()
    current_date = now.strftime("%Y-%m-%d")
    
    # Créer des tranches horaires similaires à celles du site précédent
    periods = [
        {"name": "De 9h à 12h", "start_hour": 9, "end_hour": 12},
        {"name": "Cet après-midi", "start_hour": 12, "end_hour": 18},
        {"name": "Ce soir", "start_hour": 18, "end_hour": 22},
        {"name": "Nuit", "start_hour": 22, "end_hour": 6}  # Jusqu'à 6h du matin le lendemain
    ]
    
    # Initialiser le résultat
    weather_data = []
    
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
    
    # Traiter chaque période
    for period in periods:
        # Calculer les heures correspondant à cette période
        hours_in_period = []
        for h in range(period["start_hour"], period["end_hour"]):
            hour = h % 24  # Gérer le cas où on passe minuit
            hours_in_period.append(hour)
        
        # Filtrer les données pour cette période
        period_temps = []
        period_apparent_temps = []
        period_precips = []
        period_winds = []
        period_gusts = []
        period_directions = []
        period_weather_codes = []
        
        for i, time_str in enumerate(data["hourly"]["time"]):
            dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
            local_hour = dt.hour
            
            if local_hour in hours_in_period:
                period_temps.append(data["hourly"]["temperature_2m"][i])
                period_apparent_temps.append(data["hourly"]["apparent_temperature"][i])
                period_precips.append(data["hourly"]["precipitation"][i])
                period_winds.append(data["hourly"]["windspeed_10m"][i])
                period_gusts.append(data["hourly"]["windgusts_10m"][i])
                period_directions.append(data["hourly"]["winddirection_10m"][i])
                period_weather_codes.append(data["hourly"]["weathercode"][i])
        
        # S'il y a des données pour cette période
        if period_temps:
            # Calculer les moyennes et maximums
            avg_temp = sum(period_temps) / len(period_temps)
            avg_apparent_temp = sum(period_apparent_temps) / len(period_apparent_temps)
            max_precip = max(period_precips)
            avg_wind = sum(period_winds) / len(period_winds)
            max_gust = max(period_gusts)
            
            # Direction moyenne du vent (approx. simplifiée)
            avg_direction = sum(period_directions) / len(period_directions)
            wind_direction_text = ""
            if 22.5 <= avg_direction < 67.5:
                wind_direction_text = "NE"
            elif 67.5 <= avg_direction < 112.5:
                wind_direction_text = "E"
            elif 112.5 <= avg_direction < 157.5:
                wind_direction_text = "SE"
            elif 157.5 <= avg_direction < 202.5:
                wind_direction_text = "S"
            elif 202.5 <= avg_direction < 247.5:
                wind_direction_text = "SO"
            elif 247.5 <= avg_direction < 292.5:
                wind_direction_text = "O"
            elif 292.5 <= avg_direction < 337.5:
                wind_direction_text = "NO"
            else:
                wind_direction_text = "N"
            
            # Code météo le plus fréquent
            most_common_code = max(set(period_weather_codes), key=period_weather_codes.count)
            weather_description = weather_codes.get(most_common_code, "Conditions inconnues")
            
            # Formatter les informations météorologiques
            period_data = {
                "période": period["name"],
                "température": f"{round(avg_temp)}°",
                "ressenti": f"{round(avg_apparent_temp)}°",
                "vent": f"{wind_direction_text} {round(avg_wind)} km/h",
                "rafales": f"Rafales {round(max_gust)} km/h",
                "direction_vent": wind_direction_text,
                "conditions": weather_description,
                "précipitations": f"{max_precip:.1f} mm" if max_precip > 0 else "Pas de précipitations"
            }
            
            weather_data.append(period_data)
    
    # Convertir les données en JSON
    weather_json = json.dumps(weather_data, ensure_ascii=False, indent=4)
    
    # # Sauvegarder dans un fichier
    # with open('meteo_valras_openmeteo.json', 'w', encoding='utf-8') as f:
    #     f.write(weather_json)
    
    # print("Données météo récupérées et sauvegardées dans 'meteo_valras_openmeteo.json'")
    # print(weather_json)
    
except requests.exceptions.RequestException as err:
    print(f"Erreur lors de la requête: {err}")
except Exception as e:
    print(f"Erreur inattendue: {e}")
    import traceback
    traceback.print_exc()