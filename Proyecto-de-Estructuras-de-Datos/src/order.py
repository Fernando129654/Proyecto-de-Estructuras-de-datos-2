"""
Courier Quest - Pedidos
EIF-207 - Estructuras de Datos
Autores: Fernando Durán Escobar y Alonso Durán Escobar
"""

import pygame
import json
from collections import deque
from datetime import datetime

TILE_SIZE = 40

class Order:
    """Clase que representa un pedido individual."""

    def __init__(self, data):
        self.id = data["id"]
        self.pickup = tuple(data["pickup"])
        self.dropoff = tuple(data["dropoff"])
        self.payout = data["payout"]
        self.deadline = datetime.fromisoformat(data["deadline"])
        self.weight = data["weight"]
        self.priority = data["priority"]
        self.release_time = data["release_time"]

        self.status = "waiting"  


    def __repr__(self):
        return f"<Order {self.id} prioridad={self.priority} peso={self.weight} estado={self.status}>"



class OrderManager:
    """Maneja la lista de pedidos disponibles y el inventario del jugador."""

    def __init__(self, json_file="data/Pedidos.json"):
        self.orders = []
        self.inventory = deque()  
        self._load_orders(json_file)

        self.pickup_image = pygame.image.load("assets/Paquete.png").convert_alpha()
        self.pickup_image = pygame.transform.scale(self.pickup_image, (TILE_SIZE, TILE_SIZE))

        self.dropoff_image = pygame.image.load("assets/Depositar.png").convert_alpha()
        self.dropoff_image = pygame.transform.scale(self.dropoff_image, (TILE_SIZE, TILE_SIZE))

    def _load_orders(self, json_file):
        """Carga pedidos desde JSON."""
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"No se encontró el archivo: {json_file}")

        for entry in data:
            self.orders.append(Order(entry))

    def accept_order(self, order_id):
        """Acepta un pedido y lo pasa al inventario."""
        for order in self.orders:
            if order.id == order_id and order.status == "waiting":
                order.status = "picked"
                self.inventory.append(order)
                return order
        return None

    def deliver_order(self, order_id):
        """Marca un pedido como entregado si está en el inventario."""
        for order in list(self.inventory):
            if order.id == order_id:
                order.status = "delivered"
                self.inventory.remove(order)
                return order
        return None

    def list_available_orders(self):
        """Devuelve los pedidos en espera."""
        return [o for o in self.orders if o.status == "waiting"]

    def list_inventory(self):
        """Devuelve los pedidos en el inventario del jugador."""
        return list(self.inventory)
    
    def draw_orders(self, surface):
        """Dibuja pickups y dropoffs en el mapa."""
        TILE_SIZE = 40

        for order in self.orders:
            if order.status == "waiting":
                surface.blit(self.pickup_image, (order.pickup[0] * TILE_SIZE, order.pickup[1] * TILE_SIZE))
            elif order.status == "picked":
                surface.blit(self.dropoff_image, (order.dropoff[0] * TILE_SIZE, order.dropoff[1] * TILE_SIZE))



    def get_order_at(self, x, y):
        """Devuelve un pedido en pickup/dropoff según la posición del jugador."""
        for order in self.orders:
            if order.status == "waiting" and order.pickup == (x, y):
                return order
            if order.status == "picked" and order.dropoff == (x, y):
                return order
        return None
