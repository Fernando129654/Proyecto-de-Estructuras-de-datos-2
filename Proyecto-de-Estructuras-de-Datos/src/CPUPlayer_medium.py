"""
Courier Quest - Jugador controlado por IA en medio
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
import math
from weather import WEATHER_MULTIPLIERS
TILE_SIZE = 40


class CPUPlayer_Medium:
    """Clase que representa al jugador controlado por IA."""

    def __init__(self, start_x=5, start_y=5, image_path="assets/CPUPlayer.png"):
        self.x = start_x
        self.y = start_y

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        self.timer = 0.0
        self.move_delay = 1.5  

        self.carrying_order = None 
        self.target=None
        self.money = 0
        self.reputacion = 70
        self.resistencia = 100

        self.estado = "Normal"
        self.time_still = 0.0
        self.descansando = False

    def update(self, dt, city, orders, weather=None):
        """Actualiza la lógica del jugador IA."""
        self.timer += dt
        self.time_still += dt

        if self.estado == "Exhausto":
            self.descansando = True
            self.recuperar(clima=weather)
            if self.resistencia >= 100:
                self.estado = "Normal"
                self.descansando = False
            return
        
        if not any(o.status == "waiting" for o in orders.orders):
            if not any(o.status == "picked" for o in orders.orders):
                self.descansando = True
                self.recuperar(pasivo=True, clima=weather)
                return
        
        if self.descansando:
            self.recuperar(clima=weather)
            if self.resistencia >= 100:
                self.estado = "Normal"
                self.descansando = False
            return

        if self.timer >= self.move_delay:
            self.timer = 0.0
            self.time_still = 0.0
            self.move(city, orders, weather)
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

    def move(self, city, orders, weather=None):
        """Movimiento segun su ruta o busca nueva si no tiene"""
        best_values = -float("inf")
        best_move = (0, 0)

        actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dx, dy in actions:
            new_x = self.x + dx
            new_y = self.y + dy

            if 0 <= new_x < city.width and 0 <= new_y < city.height:
                if not city.is_blocked(new_x, new_y):
                    value = self.evaluate_position((new_x, new_y), city, orders, weather,depth=2)
                    if value > best_values:
                        best_values = value
                        best_move = (dx, dy)
        self.x += best_move[0]
        self.y += best_move[1]

    
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
        """Comprueba si tiene de recoger o entregar pedidos."""

        if self.carrying_order is None:
            for order in orders.orders:
                if order.status == "waiting" and (self.x, self.y) == order.pickup:
                    order.status = "picked"
                    self.carrying_order = order
                    break
        else:
            if (self.x, self.y) == self.carrying_order.dropoff:
                self.carrying_order.status = "delivered"
                self.money += self.carrying_order.payout
                self.reputacion = min(100, self.reputacion + 3)
                self.carrying_order = None



    def evaluate_position(self, pos, city, orders, clima, depth):
        """Evalua un estado con Expectimax"""
        if depth == 0:
            return self.utility(pos, orders, clima)
    
        expected_value = 0

        for prob, next_clima in self.get_chance_events(clima):
            value = self.evaluate_position(pos, city, orders, next_clima, depth - 1)
            expected_value += prob * value

        return expected_value
    
    def get_chance_events(self,clima_actual):
        """Evalua las probabilidades de cambio de clima"""
        clima_posible = ["clear", "clouds", "rain", "storm", "wind", "heat"]
        weights = {
            "clear": [0.6, 0.2, 0.1, 0.05, 0.05, 0.0],
            "clouds": [0.3, 0.4, 0.2, 0.05, 0.05, 0.0],
            "rain": [0.2, 0.3, 0.3, 0.1, 0.1, 0.0],
            "storm": [0.1, 0.2, 0.3, 0.3, 0.1, 0.0],
            "wind": [0.3, 0.3, 0.2, 0.05, 0.15, 0.0],
            "heat": [0.2, 0.2, 0.1, 0.05, 0.05, 0.4],
        }
        probs = weights.get(clima_actual, [0.5] * len(clima_posible))
        probs = [p / sum(probs) for p in probs]
        return list(zip(probs, clima_posible))

    def utility(self, pos, orders, clima):
        """Evalúa qué tan buena es una posición."""
        px, py = pos

        if self.carrying_order:
            tx, ty = self.carrying_order.dropoff
        else:
            pickups = [o.pickup for o in orders.orders if o.status == "waiting"]
            if not pickups:
                return 0
            tx, ty = min(pickups, key=lambda p: math.dist((px, py), p))

        dist = math.dist((px, py), (tx, ty))

        clima_penalty = WEATHER_MULTIPLIERS.get(clima, 1.0)

        score = (100 - dist * 5) * clima_penalty * (self.resistencia / 100)
        return max(score,0)
    
