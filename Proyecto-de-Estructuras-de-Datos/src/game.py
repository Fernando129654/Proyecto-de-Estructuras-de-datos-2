"""
Courier Quest - Clase principal del juego
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
from city import City
from player import Player
from order import OrderManager
from weather import Weather
from datetime import datetime, timedelta
from CPUPlayer import CPUPlayer
from CPUPlayer_medium import CPUPlayer_Medium
from CPUPlayer_dificil import CPUPlayer_Dificil
import json
import os
TILE_SIZE = 40
FPS = 60
HUD_ESTADISTICAS = 120   
DURATION= 15 * 60


class Game:
    """Clase que maneja el bucle principal del juego."""

    def __init__(self):
        pygame.init()

        self.city = City()  

        self.screen = pygame.display.set_mode(
            (self.city.width * TILE_SIZE, self.city.height * TILE_SIZE + HUD_ESTADISTICAS)
        )
        pygame.display.set_caption("Courier Quest")

        self.time=0.0
        self.start_time = datetime(2025,9,1,6,0,0)

        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player(start_x=1, start_y=1)

        self.orders = OrderManager()

        self.money = 0

        self.weather = Weather("data/clima.json")

        self.fin= False

        self.score = 0

        self.cpu = CPUPlayer(start_x=1, start_y=1)



    def run(self):
        """Ejecuta el bucle principal del juego."""
        while self.running:
            dt = self.clock.get_time() / 1000.0
            self.handle_events()
            self.render()
            self.update(dt)
            self.clock.tick(FPS)

        pygame.quit()

    def handle_events(self):
        """Procesa eventos de teclado y salida."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            if self.fin:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.__init__()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                return
            
            elif event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.player.mover(0, -1, self.city, clima = self.weather.get_current_condition())
                elif event.key == pygame.K_DOWN:
                    self.player.mover(0, 1, self.city, clima = self.weather.get_current_condition())
                elif event.key == pygame.K_LEFT:
                    self.player.mover(-1, 0, self.city, clima = self.weather.get_current_condition())
                elif event.key == pygame.K_RIGHT:
                    self.player.mover(1, 0, self.city, clima = self.weather.get_current_condition())
                elif event.key == pygame.K_e:
                    self.interact()

    def interact(self):
        """Interacción del jugador con pickups o dropoffs."""
        order = self.orders.get_order_at(self.player.x, self.player.y)
        if not order:
            return

        if order.status == "waiting":
            accepted = self.orders.accept_order(order.id)
            if accepted:
                self.player.peso_total += order.weight

        elif order.status == "picked":
            delivered = self.orders.deliver_order(order.id)
            if delivered:
                self.player.peso_total -= order.weight
                self.player.reputacion += 3
                if self.player.reputacion > 100:
                    self.player.reputacion = 100
                self.money += order.payout

    def render(self):
        """Dibuja la escena en pantalla."""
        self.screen.fill((0, 0, 0))
        if self.fin:
            self.draw_fin()
        else:
            self.city.draw(self.screen)

            self.orders.draw_orders(self.screen)

            self.player.draw(self.screen)

            self.draw_hud()

        self.cpu.draw(self.screen)
        pygame.display.flip()

    def draw_hud(self):
        """Dibuja el HUD en la parte inferior de la pantalla."""
        hud_y = self.city.height * TILE_SIZE + 10
        pygame.draw.rect(self.screen, (50, 50, 50),
                         (0, self.city.height * TILE_SIZE,
                          self.city.width * TILE_SIZE, HUD_ESTADISTICAS))

        self.player.draw_stats(self.screen, offset_y=hud_y)

        font = pygame.font.SysFont(None, 28)
        money_text = font.render(f"Ingresos: {self.money}", True, (255, 255, 0))
        self.screen.blit(money_text, (250, hud_y))

        goal_text = font.render(f"Meta: {self.city.goal}", True, (0, 255, 255))
        self.screen.blit(goal_text, (250, hud_y + 30))


        font_small = pygame.font.SysFont(None, 22)
        inv_x = 500  
        inv_y = hud_y + 5
        inv_text = font_small.render("Inventario:", True, (255, 255, 255))
        self.screen.blit(inv_text, (inv_x, inv_y))

        max_width = self.city.width * TILE_SIZE - inv_x - 20

        for i, order in enumerate(self.orders.list_inventory()[:3]):
            txt = f"{order.id} Ubicacion: {order.dropoff} (peso {order.weight})"
            text_surface = font_small.render(txt, True, (200, 200, 200))

            
            if text_surface.get_width() > max_width:
                while text_surface.get_width() > max_width and len(txt) > 5:
                    txt = txt[:-1]
                    text_surface = font_small.render(txt + "...", True, (200, 200, 200))

            self.screen.blit(text_surface, (inv_x, inv_y + 20 + i * 20))

        current_time = self.start_time + timedelta(seconds=int(self.time))
        time_text=font.render(f"Hora: {current_time.strftime('%H:%M:%S')}", True, (255, 255, 255))
        self.screen.blit(time_text,(250,hud_y+60))

        clima_text = font.render(f"Clima: {self.weather.get_current_condition()}",
                                 True, (200, 200, 255))
        self.screen.blit(clima_text, (500, hud_y + 70))

    def update(self, dt):
        """Actualiza la lógica del juego."""
        if self.time >= DURATION:
            self.trigger_fin("Tiempo agotado. No alcanzaste la meta.", victory=False)
            return


        if self.player.reputacion <= 20:
            self.trigger_fin("Tu reputación cayó demasiado. ¡Has sido despedido!", victory=False)
            return

        if self.money >= self.city.goal:
            self.trigger_fin("¡Has alcanzado la meta de ingresos!", victory=True)
            return

        self.time += dt

        current_time = self.start_time + timedelta(seconds=int(self.time))

        keys = pygame.key.get_pressed()
        if not (keys[pygame.K_UP] or keys[pygame.K_DOWN] or
                keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]):
            self.player.recuperar(dt)

        self.weather.update(self.time)

        for order in list(self.orders.inventory):
            if order.status == "picked" and current_time > order.deadline:
                order.status = "expired"
                self.orders.inventory.remove(order)
                self.player.reputacion -= 6
                if self.player.reputacion < 0:
                    self.player.reputacion = 0

        self.cpu.update(dt,self.city, self.orders, self.weather.get_current_condition())

    def trigger_fin(self, reason, victory=False):
        """Detiene el juego y muestra la pantalla de Game Over o Victoria."""
        self.fin = True
        self.running = False


        if victory:
            tiempo_bonus = max(0, DURATION - int (self.time))
            self.score = self.money + tiempo_bonus
            self.save_score()

        self.draw_fin(reason, victory)

    def draw_fin(self, reason, victory=False):
        """Muestra la pantalla final (Game Over o Victoria) con el top 5 de puntajes."""
        self.screen.fill((0, 0, 0))
        font_big = pygame.font.SysFont(None, 60)
        font_small = pygame.font.SysFont(None, 30)
        font_score = pygame.font.SysFont(None, 26)

        if victory:
            title_text = font_big.render("¡Victoria!", True, (0, 255, 0))
            score_text = font_small.render(
                f"Tu puntuación final: {self.score}", True, (255, 255, 255))
        else:
            title_text = font_big.render("Game Over", True, (255, 0, 0))
            score_text = font_small.render(reason, True, (255, 255, 255))

        self.screen.blit(title_text, (self.city.width * TILE_SIZE // 2 - 120,
                                  self.city.height * TILE_SIZE // 2 - 150))
        self.screen.blit(score_text, (self.city.width * TILE_SIZE // 2 - 150,
                                  self.city.height * TILE_SIZE // 2 - 100))

        try:
            with open("data/scores.json", "r", encoding="utf-8") as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = []

        rank_title = font_small.render("Mejores 5 Puntajes", True, (255, 215, 0))
        self.screen.blit(rank_title, (self.city.width * TILE_SIZE // 2 - 130,
                                  self.city.height * TILE_SIZE // 2 - 50))

        y_offset = self.city.height * TILE_SIZE // 2 - 20

        for i, s in enumerate(scores[:5]):
            text = f"{i+1}. {s['player']} — {s['score']} pts ({s['money']}, {s['time_left']}s)"
            color = (255, 255, 255) if i > 0 else (0, 255, 255)  
            score_line = font_score.render(text, True, color)
            self.screen.blit(score_line, (self.city.width * TILE_SIZE // 2 - 180, y_offset))
            y_offset += 30


        instr_text = font_small.render("Presiona ESC para salir", True, (200, 200, 200))
        self.screen.blit(instr_text, (self.city.width * TILE_SIZE // 2 - 120, y_offset + 40))

        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    waiting = False

    def save_score(self):
        """Guarda el puntaje en un archivo local y mantiene el ranking ordenado."""
        file_path = "data/scores.json"

        if not os.path.exists("data"):
            os.makedirs("data")

        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    scores = json.load(f)
                except json.JSONDecodeError:
                    scores = []
        else:
            scores = []

        tiempo_total_seg = DURATION
        tiempo_sobrante = max(0, tiempo_total_seg - int(self.time))

        new_score = {
            "player": "Jugador1",
            "score": self.score,
            "money": self.money,
            "time_left": tiempo_sobrante,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


        scores.append(new_score)
        scores = sorted(scores, key=lambda x: x["score"], reverse=True)

        with open(file_path, "w", encoding="utf-8") as f:

            json.dump(scores, f, ensure_ascii=False, indent=4)
