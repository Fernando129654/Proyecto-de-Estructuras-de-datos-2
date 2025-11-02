import json
import random


WEATHER_MULTIPLIERS = {
    "clear": 1.00,
    "clouds": 0.98,
    "rain_light": 0.90,
    "rain": 0.85,
    "storm": 0.75,
    "fog": 0.88,
    "wind": 0.92,
    "heat": 0.90,
    "cold": 0.92
}


class Weather:
    """Maneja el clima usando ráfagas definidas en un archivo JSON."""

    def __init__(self, json_file="data/clima.json"):
        self.current_condition = "clear"
        self.intensity = 1.0
        self.duration = 60
        self.start_time = 0

        self.bursts = []
        self.burst_index = 0
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.bursts = data.get("bursts", [])
        except FileNotFoundError:
            self.bursts = [{"duration_sec": 60, "condition": "clear", "intensity": 1.0}]

        if self.bursts:
            self._apply_burst(0)

    def _apply_burst(self, index):
        """Aplica un burst de la lista."""
        burst = self.bursts[index]
        self.current_condition = burst["condition"]
        self.duration = burst["duration_sec"]
        self.intensity = burst["intensity"]
        self.start_time = 0
        self.burst_index = index

    def update(self, game_time):
        """
        Actualiza el clima según el tiempo de juego (segundos).
        game_time: tiempo total desde inicio de la partida.
        """
        elapsed = game_time - self.start_time
        if elapsed >= self.duration:
            next_index = (self.burst_index + 1) % len(self.bursts)
            self._apply_burst(next_index)
            self.start_time = game_time 

    def get_current_condition(self):
        """Devuelve el nombre de la condición climática actual."""
        return self.current_condition
