#!/usr/bin/env python3
"""
Analyse météo simple pour Paris
Version condensée avec tout dans un fichier
"""

import requests

# Configuration
PARIS_LAT = 48.85
PARIS_LON = 2.35
API_URL = "https://api.open-meteo.com/v1/forecast"

def get_weather_data():
    params = {
        "latitude": PARIS_LAT,
        "longitude": PARIS_LON,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": "Europe/Paris",
        "forecast_days": 7
    }
    
    response = requests.get(API_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Erreur API: {response.status_code}")
    
    return response.json()

def main():
    print("Analyse meteo Paris")
        
    try:
        raw_data = get_weather_data()
        
        print(raw_data)
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
