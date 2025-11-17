"""
Courier Quest - Jugador controlado por IA en Difícil
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
import heapq
import math
from weather import WEATHER_MULTIPLIERS
TILE_SIZE = 40


class CPUPlayer_Dificil:
    """Clase que representa al jugador controlado por IA."""

    def __init__(self, start_x=5, start_y=5, image_path="assets/CPUPlayer.png"):
        self.x = start_x
        self.y = start_y

        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        self.path = []

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
        self.timer += 0.06
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
        if not self.path:
            self.plan_path(city, orders)
            return 
        
        next_x, next_y = self.path.pop(0)
        if not city.is_blocked(next_x, next_y):
            self.x, self.y = next_x, next_y
            self._consumir_resistencia(city, clima=weather)
        
        self.check_orders(orders)

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



    def plan_path(self, city, orders):
        """Calcula una nueva ruta hacia la entrga o recogida del paquete."""
        if self.carrying_order:
            goal=self.carrying_order.dropoff
        else:
            waiting = [o for o in orders.orders if o.status == "waiting"]
            if not waiting:
                self.path = []
                return
            
            goal=min(waiting, key=lambda o: math.dist((self.x, self.y), o.pickup)).pickup

        self.path = self.a_star_search((self.x, self.y), goal, city)

    
    def a_star_search(self, start, goal,city):
        """El algoritmo A*"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}

        while open_set:
            _, current = heapq.heappop(open_set)

            if current == goal:
                return self.reconstruct_path(came_from, current)

            x,y = current
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x + dx, y + dy

                if not (0 <= nx < city.width and 0 <= ny < city.height):
                    continue
                if city.is_blocked(nx, ny):
                    continue
                
                tentative_g = g_score[current] + 1
                neighbor = (nx, ny)

                if tentative_g < g_score.get(neighbor, float('inf')):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        return []


    def heuristic(self, a, b):
        """Distancia Manhattan."""
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def reconstruct_path(self, came_from, current):
        """Reconstruye el camino desde el nodo objetivo al inicio."""
        path= []
        while current in came_from:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path