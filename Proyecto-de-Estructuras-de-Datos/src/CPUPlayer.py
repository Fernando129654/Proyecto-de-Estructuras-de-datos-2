"""
Courier Quest - Jugador controlado por IA en facil
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
import random
from weather import WEATHER_MULTIPLIERS
TILE_SIZE = 40


class CPUPlayer:
    """Clase que representa al jugador controlado por IA."""

    def __init__(self, start_x=5, start_y=5, image_path="assets/CPUPlayer.png"):
        self.x = start_x
        self.y = start_y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.timer = 0.0
        self.move_delay = 1.5  
        self.carrying_order = None 
        self.money = 0
        self.reputacion = 70
        self.resistencia = 100
        self.estado = "Normal"
        self.time_still = 0.0
        self.descansando = False

    def update(self, dt, city, orders, weather=None):
        """Lógica de movimiento simple (aleatorio o básico)."""
        self.timer += dt+0.03
        self.time_still += dt

        if self.estado == "Exhausto":
            self.descansando = True
            self.recuperar(clima=weather)
            if self.resistencia >= 100:
                self._actualizar_estado()
                self.descansando = False
            return
        
        if self.descansando:
            self.recuperar(clima=weather)
            if self.resistencia >= 100:
                self._actualizar_estado()
                self.descansando = False
            return

        if not any(o.status == "waiting" for o in orders.orders):
            if not any(o.status == "picked" for o in orders.orders):
                self.descansando = True
                self.recuperar(pasivo=True, clima=weather)
                return
        

        if self.timer >= self.move_delay:
            self.timer = 0.0
            self.random_move(city)
            self.time_still = 0.0
            self._consumir_resistencia(city,clima=weather)
            self.check_orders(orders)
        self.recuperar(pasivo=True, clima=weather)


    def draw(self, surface):
        """Dibuja al jugador CPU en pantalla."""
        surface.blit(self.image,(self.x * TILE_SIZE, self.y * TILE_SIZE))

    def draw_stats(self, surface, offset_y=0):
        """Dibuja sus estadísticas (resistencia y reputación)."""
        font = pygame.font.SysFont(None, 22)
        res_ratio = self.resistencia / 100
        rep_ratio = self.reputacion / 100

        pygame.draw.rect(surface, (150, 150, 150),
                         (10, offset_y, 200, 10))
        pygame.draw.rect(surface, (255, 165, 0),
                         (10, offset_y, 200 * res_ratio, 10))
        surface.blit(font.render(f"CPU Resistencia: {int(self.resistencia)}",
                                 True, (255, 255, 255)), (220, offset_y - 5))

        pygame.draw.rect(surface, (150, 150, 150),
                         (10, offset_y + 25, 200, 10))
        pygame.draw.rect(surface, (255, 215, 0),
                         (10, offset_y + 25, 200 * rep_ratio, 10))
        surface.blit(font.render(f"CPU Reputación: {int(self.reputacion)}",
                                 True, (255, 255, 255)), (220, offset_y + 20))

    def random_move(self, city):
        """Movimiento aleatorio básico."""
        dx, dy = random.choice([(1, 0), (-1, 0), (0, 1), (0, -1)])
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < city.width and 0 <= new_y < city.height:
            if not city.is_blocked(new_x, new_y):
                self.x = new_x
                self.y = new_y
    
    def _consumir_resistencia(self,city, clima=None):
        """Reduce la resistencia por movimiento."""
        consumo = 0.5 

        if clima and clima in WEATHER_MULTIPLIERS:
            consumo *= 1.0 / WEATHER_MULTIPLIERS[clima]

        symbol = city.tiles[self.y][self.x]
        surface_weight = city.legend[symbol].get("surface_weight", 1.0)
        consumo *= 1.0 / surface_weight

        self.resistencia -= consumo
        self._actualizar_estado()

    def recuperar(self, pasivo=False, clima=None):
        """Recupera resistencia si está quieto."""

        if self.time_still > 3.0:
            if self.resistencia < 100:
                if pasivo:
                    self.resistencia += 5
                else:
                    self.resistencia += 2.5

                if self.resistencia > 100:
                    self.resistencia = 100
        self._actualizar_estado()

    def _actualizar_estado(self):
        """Actualiza el estado según la resistencia actual."""
        if self.resistencia <= 0:
            self.resistencia = 0
            self.estado = "Exhausto"
        elif self.resistencia < 30:
            self.estado = "Cansado"
        else:
            self.estado = "Normal"

    def check_orders(self, orders):
        """Comprueba si el CPU recoge o entrega pedidos."""

        active_orders = [o for o in orders.orders if o.status in ("waiting", "picked")]


        if self.carrying_order is None:
            for order in active_orders:
                if order.status == "waiting" and (self.x, self.y) == order.pickup:
                    order.status = "picked"
                    self.carrying_order = order
                    print(f"[CPU] Pedido {order.id} recogido.")
                    break


        elif self.carrying_order is not None:
            order = self.carrying_order
            if (self.x, self.y) == order.dropoff:
                order.status = "delivered"
                self.money += order.payout
                self.reputacion = min(100, self.reputacion + 3)
                print(f"[CPU] Pedido {order.id} entregado. Ganó {order.payout} monedas.")
                self.carrying_order = None


        elif self.carrying_order is not None:
            order = self.carrying_order
            if (self.x, self.y) == order.dropoff:
                order.status = "delivered"
                self.money += order.payout
                self.reputacion = min(100, self.reputacion + 3)
                print(f"[CPU] Pedido {order.id} entregado. Ganó {order.payout} monedas.")
                self.carrying_order = None