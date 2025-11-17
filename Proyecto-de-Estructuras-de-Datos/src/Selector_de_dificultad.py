import pygame
from game import Game
from CPUPlayer import CPUPlayer
from CPUPlayer_medium import CPUPlayer_Medium
from CPUPlayer_dificil import CPUPlayer_Dificil

TILE_SIZE = 40
HUD_ESTADISTICAS = 120
FPS = 60


class Selector_De_Dificultad:
    """Pantalla inicial para seleccionar dificultad."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Courier Quest - Selección de Dificultad")

        self.clock = pygame.time.Clock()
        self.running = True
        self.selected_difficulty = None

        self.font_title = pygame.font.SysFont(None, 60)
        self.font_button = pygame.font.SysFont(None, 40)
 
        self.buttons = [
            pygame.Rect(250, 200, 300, 60),
            pygame.Rect(250, 300, 300, 60),
            pygame.Rect(250, 400, 300, 60)
        ]
        self.labels = ["Fácil", "Media", "Difícil"]

    def run(self):
        """Bucle principal de la pantalla."""
        while self.running:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

            if self.selected_difficulty:
                self.start_game()
                self.running = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.check_button_click(event.pos)

    def check_button_click(self, mouse_pos):
        """Detecta cuál botón fue presionado."""
        for i, rect in enumerate(self.buttons):
            if rect.collidepoint(mouse_pos):
                self.selected_difficulty = self.labels[i]
                return

    def draw(self):
        """Dibuja los botones y el título."""
        self.screen.fill((20, 20, 20))

        title = self.font_title.render("Selecciona la dificultad", True, (255, 255, 255))
        self.screen.blit(title, (180, 100))

        for i, rect in enumerate(self.buttons):
            color = (100, 100, 255) if self.labels[i] == self.selected_difficulty else (70, 70, 70)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            pygame.draw.rect(self.screen, (255, 255, 255), rect, 3, border_radius=10)

            label = self.font_button.render(self.labels[i], True, (255, 255, 255))
            self.screen.blit(label, (rect.x + 110, rect.y + 10))

        pygame.display.flip()

    def start_game(self):
        """Crea el objeto Game con la CPU seleccionada."""
        game = Game()

        if self.selected_difficulty == "Fácil":
            game.cpu = CPUPlayer(start_x=1, start_y=1)
        elif self.selected_difficulty == "Media":
            game.cpu = CPUPlayer_Medium(start_x=1, start_y=1)
        elif self.selected_difficulty == "Difícil":
            game.cpu = CPUPlayer_Dificil(start_x=1, start_y=1)

        game.run()
