#!/usr/bin/env python3
"""
Analyse météo simple pour Paris
Version condensée avec tout dans un fichier
"""

import requests
import statistics
import json
from datetime import datetime
import matplotlib.pyplot as plt

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

def test_analyze_basic():
    max_temps = [20, 22, 18, 25, 21, 19, 23]
    min_temps = [12, 14, 10, 17, 13, 11, 15]
    
    analysis = analyze_temperatures(max_temps, min_temps)
    
    assert analysis["temperature_moyenne_max"] == 21.1
    assert analysis["temperature_moyenne_min"] == 13.1
    assert analysis["temperature_max_absolue"] == 25
    assert analysis["temperature_min_absolue"] == 10
    assert analysis["amplitude_moyenne"] == 8.0
    assert analysis["tendance"] == "temperatures en hausse"
    print("Test basique: OK")

def test_analyze_tendances():
    max_hausse = [15, 16, 17, 18, 19, 20, 21]
    min_hausse = [10, 11, 12, 13, 14, 15, 16]
    result = analyze_temperatures(max_hausse, min_hausse)
    assert result["tendance"] == "temperatures en hausse"
    
    max_baisse = [25, 24, 23, 22, 21, 20, 19]
    min_baisse = [18, 17, 16, 15, 14, 13, 12]
    result = analyze_temperatures(max_baisse, min_baisse)
    assert result["tendance"] == "temperatures en baisse"
    
    max_stable = [20, 21, 19, 22, 18, 21, 20]
    min_stable = [15, 16, 14, 17, 13, 16, 15]
    result = analyze_temperatures(max_stable, min_stable)
    assert result["tendance"] == "temperatures stables"
    
    print("Test tendances: OK")

def test_analyze_cas_limites():
    max_negatif = [-5, -3, -8, -1, -4, -6, -2]
    min_negatif = [-12, -10, -15, -8, -11, -13, -9]
    result = analyze_temperatures(max_negatif, min_negatif)
    assert result["temperature_max_absolue"] == -1
    assert result["temperature_min_absolue"] == -15
    
    max_egal = [20, 20, 20, 20, 20, 20, 20]
    min_egal = [15, 15, 15, 15, 15, 15, 15]
    result = analyze_temperatures(max_egal, min_egal)
    assert result["temperature_moyenne_max"] == 20.0
    assert result["amplitude_moyenne"] == 5.0
    assert result["tendance"] == "temperatures stables"
    
    max_extreme = [50, 45, 48, 52, 47, 49, 51]
    min_extreme = [35, 30, 33, 37, 32, 34, 36]
    result = analyze_temperatures(max_extreme, min_extreme)
    assert result["temperature_max_absolue"] == 52
    assert result["amplitude_moyenne"] == 15.0
    
    print("Test cas limites: OK")

def test_analyze_precision():
    max_decimal = [20.1, 22.7, 18.3, 25.9, 21.4, 19.6, 23.2]
    min_decimal = [12.5, 14.8, 10.2, 17.1, 13.7, 11.9, 15.3]
    
    result = analyze_temperatures(max_decimal, min_decimal)
    
    assert isinstance(result["temperature_moyenne_max"], float)
    assert len(str(result["temperature_moyenne_max"]).split('.')[-1]) <= 1
    assert len(str(result["amplitude_moyenne"]).split('.')[-1]) <= 1
    
    print("Test précision: OK")

def test_api_integration():
    try:
        data = get_weather_data()
        
        assert "daily" in data
        assert "time" in data["daily"]
        assert "temperature_2m_max" in data["daily"]
        assert "temperature_2m_min" in data["daily"]
        assert "precipitation_sum" in data["daily"]
        
        assert len(data["daily"]["time"]) == 7
        assert len(data["daily"]["temperature_2m_max"]) == 7
        assert len(data["daily"]["temperature_2m_min"]) == 7
        
        max_temps = data["daily"]["temperature_2m_max"]
        min_temps = data["daily"]["temperature_2m_min"]
        for i in range(len(max_temps)):
            assert max_temps[i] >= min_temps[i], f"Jour {i}: max < min"
        
        print("Test API intégration: OK")
        
    except requests.exceptions.RequestException:
        print("Test API: ECHEC (pas de connexion internet)")
    except Exception as e:
        print(f"Test API: ECHEC ({e})")

def test_save_load_json():
    test_weather_data = {
        "daily": {
            "time": ["2025-07-02", "2025-07-03"],
            "temperature_2m_max": [25.0, 23.0],
            "temperature_2m_min": [15.0, 13.0],
            "precipitation_sum": [0.0, 2.5]
        }
    }
    
    test_analysis = {
        "temperature_moyenne_max": 24.0,
        "precipitation_totale": 2.5
    }
    
    save_results(test_weather_data, test_analysis)
    
    try:
        with open("meteo.json", "r", encoding="utf-8") as f:
            loaded_data = json.load(f)
        
        assert "date_analyse" in loaded_data
        assert "lieu" in loaded_data
        assert "donnees_brutes" in loaded_data
        assert "analyse" in loaded_data
        assert loaded_data["lieu"] == "Paris"
        
        print("Test sauvegarde JSON: OK")
        
    except Exception as e:
        print(f"Test sauvegarde JSON: ECHEC ({e})")

def run_all_tests():
    print("=== TESTS UNITAIRES ===")
    test_analyze_basic()
    test_analyze_tendances()
    test_analyze_cas_limites()  
    test_analyze_precision()
    
    print("\n=== TESTS D'INTÉGRATION ===")
    test_api_integration()
    test_save_load_json()

def create_graph(dates, max_temps, min_temps):
    plt.figure(figsize=(10, 6))
    
    dates_obj = [datetime.fromisoformat(date) for date in dates]
    
    plt.plot(dates_obj, max_temps, 'r-o', label='Temperature max', linewidth=2)
    plt.plot(dates_obj, min_temps, 'b-o', label='Temperature min', linewidth=2)
    
    plt.fill_between(dates_obj, min_temps, max_temps, alpha=0.3, color='lightgray')
    
    plt.title('Previsions meteo Paris - 7 jours')
    plt.xlabel('Date')
    plt.ylabel('Temperature (°C)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    plt.savefig('temperatures.png', dpi=150)
    plt.show()
    
# def run_tests():    
#     test_max = [20, 22, 18, 25, 21, 19, 23]
#     test_min = [12, 14, 10, 17, 13, 11, 15]
    
#     analysis = analyze_temperatures(test_max, test_min)
#     assert analysis["temperature_moyenne_max"] == 21.1
#     assert analysis["temperature_max_absolue"] == 25
#     print("Test analyse: OK")
    
#     try:
#         data = get_weather_data()
#         assert "daily" in data
#         print("Test API: OK")
#     except:
#         print("Test API: ECHEC (verifiez votre connexion)")
    
def main():
    print("Analyse meteo Paris\n")

    # run_tests()
    run_all_tests()
        
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

        create_graph(dates, max_temps, min_temps)
        
        print(f"{raw_data} \n")
        print(f"{analysis}\n")
        
    except Exception as e:
        print(f"Erreur: {e}")

if __name__ == "__main__":
    main()
