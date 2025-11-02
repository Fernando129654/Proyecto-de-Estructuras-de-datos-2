"""
Courier Quest - Carga de datos remotos
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import os
import json
import requests

CITY_API_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/GET/city/map"
ORDERS_API_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/GET/city/jobs"
WEATHER_API_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/GET/city/weather"

DATA_FOLDER = "data"
CITY_FILE = os.path.join(DATA_FOLDER, "Info_de_ciudad.json")
ORDERS_FILE = os.path.join(DATA_FOLDER, "Pedidos.json")
WEATHER_FILE = os.path.join(DATA_FOLDER, "clima.json")


def fetch_and_save(url, local_file):
    """Descarga un archivo JSON desde una API y lo guarda localmente."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        os.makedirs(os.path.dirname(local_file), exist_ok=True)

        with open(local_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        return True

    except requests.RequestException as e:
        return False


def fetch_all_data():
    """Intenta actualizar ciudad, pedidos y clima desde las APIs."""

    fetch_and_save(CITY_API_URL, CITY_FILE)
    fetch_and_save(ORDERS_API_URL, ORDERS_FILE)
    fetch_and_save(WEATHER_API_URL, WEATHER_FILE)



if __name__ == "__main__":
    fetch_all_data()
