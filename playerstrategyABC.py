from abc import ABC, abstractmethod


class PlayerStrategy(ABC):
    """Interfaz abstracta para estrategias de jugadores"""

    @abstractmethod
    def get_name(self):
        """Retorna el nombre del jugador"""
        pass

    @abstractmethod
    def make_decision(self, player_cards, board_cards, available_actions):
        """
        Toma una decisión basada solo en las cartas del jugador y las cartas comunitarias

        Args:
            player_cards: Lista de cartas del jugador
            board_cards: Lista de cartas comunitarias en la mesa
            available_actions: Lista de acciones disponibles [(action_type, description, amount), ...]

        Returns:
            Tupla (action_type, amount) o None para cancelar
        """
        pass

    @abstractmethod
    def on_action_taken(self, player_index, action_type, amount, description):
        """
        Callback cuando se toma una acción (para logging, análisis, etc.)

        Args:
            player_index: Índice del jugador que tomó la acción
            action_type: Tipo de acción tomada
            amount: Cantidad apostada
            description: Descripción de la acción
        """
        pass
