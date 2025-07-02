#!/usr/bin/env python3
"""
Analyse météo simple pour Paris
Version condensée avec tout dans un fichier
"""

import requests
import statistics
import json
from datetime import datetime

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


def analyze_temperatures(max_temps, min_temps):
    analysis = {
        "temperature_moyenne_max": round(statistics.mean(max_temps), 1),
        "temperature_moyenne_min": round(statistics.mean(min_temps), 1),
        "temperature_max_absolue": max(max_temps),
        "temperature_min_absolue": min(min_temps),
        "amplitude_moyenne": round(statistics.mean([max_temps[i] - min_temps[i] for i in range(len(max_temps))]), 1)
    }
    
    if max_temps[-1] > max_temps[0]:
        analysis["tendance"] = "temperatures en hausse"
    elif max_temps[-1] < max_temps[0]:
        analysis["tendance"] = "temperatures en baisse"  
    else:
        analysis["tendance"] = "temperatures stables"
    
    return analysis

def save_results(weather_data, analysis):
    results = {
        "date_analyse": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "lieu": "Paris",
        "donnees_brutes": weather_data,
        "analyse": analysis
    }
    
    with open("meteo.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
def main():
    print("Analyse meteo Paris\n")
        
    try:
        raw_data = get_weather_data()

        daily = raw_data["daily"]
        dates = daily["time"]
        max_temps = daily["temperature_2m_max"]
        min_temps = daily["temperature_2m_min"]
        precipitations = daily["precipitation_sum"]

        analysis = analyze_temperatures(max_temps, min_temps)
        analysis["precipitation_totale"] = round(sum(precipitations), 1)
        
        save_results(raw_data, analysis)
        
        print(f"{raw_data} \n")
        print(f"{analysis}\n")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
