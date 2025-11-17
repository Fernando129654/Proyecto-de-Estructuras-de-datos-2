"""
Courier Quest - Juego de entregas
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""
from Cargar_api import fetch_all_data
from Selector_de_dificultad import Selector_De_Dificultad

def main():
    """Punto de entrada del juego."""
    fetch_all_data()
    
    selector = Selector_De_Dificultad()
    selector.run()



if __name__ == "__main__":
    main()

