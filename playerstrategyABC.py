from abc import ABC, abstractmethod


class PlayerStrategy(ABC):
    """Interfaz abstracta para estrategias de jugadores"""

    @abstractmethod
    def get_name(self):
        """Retorna el nombre del jugador"""
        pass

    @abstractmethod
    def make_decision(self, game_state, available_actions, player_index):
        """
        Toma una decisión basada en el estado del juego

        Args:
            game_state: Estado actual del juego
            available_actions: Lista de acciones disponibles [(action_type, description, amount), ...]
            player_index: Índice del jugador en el juego

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
