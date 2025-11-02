"""
Lector de la ciudad
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import json
import pygame

TILE_SIZE = 40


class City:
    """Clase que maneja el mapa de la ciudad."""

    def __init__(self, json_file="data/Info_de_ciudad.json"):
        pygame.init()
        pygame.display.set_mode((1, 1))
        self.width = 0
        self.height = 0
        self.tiles = []
        self.legend = {}
        self.goal = 0

        self._load_map(json_file)

        self.textures= {
            "calle": pygame.image.load("assets/Calle.png").convert(),
            "edificio": pygame.image.load("assets/Ciudad.png").convert(),
            "parque": pygame.image.load("assets/Parque.png").convert(),
        }

        for key in self.textures:
            self.textures[key] = pygame.transform.scale(
                self.textures[key], (TILE_SIZE, TILE_SIZE)
            )

        self.background = self._generate_background()


    def _load_map(self, json_file):
        """Carga el mapa desde un archivo JSON."""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {json_file}")

        self.width = data["width"]
        self.height = data["height"]
        self.tiles = data["tiles"]
        self.legend = data["legend"]
        self.goal = data.get("goal", 0)

    def is_blocked(self, x, y):
        """Vefica si es un edificio"""
        symbol = self.tiles[y][x]
        return self.legend[symbol].get("blocked", False)

    def draw(self, surface):
        """Dibuja la ciudad."""        
        for y in range(self.height):
            for x in range(self.width):
                symbol = self.tiles[y][x]
                tile_type = self.legend[symbol]["name"]
                image = self.textures.get(tile_type)

                if image:
                    surface.blit(image, (x * TILE_SIZE, y * TILE_SIZE))
                else:
                    pygame.draw.rect(surface, (255, 0, 255),
                             (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    def _generate_background(self):
        """Genera un fondo de base donde se colocarán las texturas."""
        # Creamos una superficie con el tamaño del mapa completo
        background = pygame.Surface((self.width * TILE_SIZE,
                                     self.height * TILE_SIZE))

        # Pintamos el fondo con un color base (ej. pasto claro)
        background.fill((130, 200, 130))

        # Podés dibujar patrones simples para hacerlo más "natural"
        for y in range(0, self.height * TILE_SIZE, TILE_SIZE):
            for x in range(0, self.width * TILE_SIZE, TILE_SIZE):
                if (x + y) // TILE_SIZE % 2 == 0:
                    pygame.draw.rect(background, (120, 190, 120),
                                     (x, y, TILE_SIZE, TILE_SIZE))
