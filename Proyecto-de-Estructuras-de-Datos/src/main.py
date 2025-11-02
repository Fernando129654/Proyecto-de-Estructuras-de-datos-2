"""
Courier Quest - Juego de entregas
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""
from Cargar_api import fetch_all_data
from game import Game

def main():
    """Punto de entrada del juego."""
    fetch_all_data()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
