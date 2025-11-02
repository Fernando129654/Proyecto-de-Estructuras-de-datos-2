"""
Courier Quest - Jugador y sus estadísticas
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
from weather import WEATHER_MULTIPLIERS
TILE_SIZE = 40


class Player:
    """Clase que representa al repartidor."""

    def __init__(self, start_x=1, start_y=1):
        self.x = start_x
        self.y = start_y

        self.resistencia = 100
        self.reputacion = 70

        self.vel_base = 1

        self.estado = "Normal"

        self.peso_total = 0

        self.time_still = 0.0

        self.image = pygame.image.load("assets/Jugador.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

    def mover(self, dx, dy, city, clima=None):
        """
        Mueve al jugador
        """
        if self.estado == "Exhausto":
            return
        new_x = self.x + dx
        new_y = self.y + dy
        if 0 <= new_x < city.width and 0 <= new_y < city.height:
            if not city.is_blocked(new_x, new_y):
                self.x = new_x
                self.y = new_y
                self._consumir_resistencia(city, clima)
                self.time_still = 0.0

    def _consumir_resistencia(self,city, clima=None):
        """Reduce la resistencia según peso y clima."""
        consumo = 0.5 

        if self.peso_total > 3:
            consumo += 0.2 * (self.peso_total - 3)

        if clima and clima in WEATHER_MULTIPLIERS:
            consumo *= 1.0 / WEATHER_MULTIPLIERS[clima]

        symbol = city.tiles[self.y][self.x]
        surface_weight = city.legend[symbol].get("surface_weight", 1.0)
        consumo *= 1.0 / surface_weight

        self.resistencia -= consumo
        self._actualizar_estado()

    def recuperar(self,dt, en_punto_descanso=False):
        """Recupera resistencia si el jugador está parado."""
        self.time_still += dt

        if self.time_still >= 3.0:  
            if self.resistencia < 100:
                if en_punto_descanso:
                    self.resistencia += 10 * dt
                else:
                    self.resistencia += 5 * dt

            if self.resistencia > 100:
                self.resistencia = 100

        self._actualizar_estado()

    def _actualizar_estado(self):
        """Actualiza el estado según la resistencia."""
        if self.resistencia <= 0:
            self.estado = "Exhausto"
            self.resistencia = 0
        elif self.resistencia <= 30:
            self.estado = "Cansado"
        else:
            self.estado = "Normal"

    def draw(self, surface):
        """Dibuja al jugador en pantalla (rectángulo azul)."""
        player_rect = pygame.Rect(
            self.x * TILE_SIZE,
            self.y * TILE_SIZE,
            TILE_SIZE,
            TILE_SIZE,
        )
        surface.blit(self.image, player_rect)

    def draw_stats(self, surface, offset_y=0):
        """Dibuja barras de resistencia y reputación en el HUD."""
        font = pygame.font.SysFont(None, 24)

        res_bar_width = 200
        res_ratio = self.resistencia / 100
        pygame.draw.rect(surface, (150, 150, 150),
            (10, offset_y, res_bar_width, 20))
        pygame.draw.rect(surface, (0, 200, 0),
            (10, offset_y, res_bar_width * res_ratio, 20))
        res_text = font.render(f"Resistencia: {int(self.resistencia)}",
            True, (255, 255, 255))
        surface.blit(res_text, (10, offset_y + 25))


        rep_bar_width = 200
        rep_ratio = self.reputacion / 100
        pygame.draw.rect(surface, (150, 150, 150),
            (10, offset_y + 60, rep_bar_width, 20))
        pygame.draw.rect(surface, (0, 0, 200),
            (10, offset_y + 60, rep_bar_width * rep_ratio, 20))
        rep_text = font.render(f"Reputación: {int(self.reputacion)}",
            True, (255, 255, 255))
        surface.blit(rep_text, (10, offset_y + 85))
