"""
Ejemplo de cómo crear jugadores personalizados para el simulador de poker
"""
from playerstrategyABC import PlayerStrategy
import random


class SimpleAIStrategy(PlayerStrategy):
    """Estrategia de IA simple con comportamiento aleatorio"""

    def __init__(self, name="Bot"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        """Implementa una IA simple para los jugadores automáticos"""
        import random

        if not available_actions:
            return None

        # IA muy básica - comportamiento aleatorio con algunas tendencias
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.2  # 20% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.6  # 60% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.15  # 15% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.05  # 5% probabilidad de all-in

            action_weights.append(weight)

        # Seleccionar acción basada en probabilidades
        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🤖 {self.name}: {description}")


class AggressiveAIStrategy(PlayerStrategy):
    """Estrategia de IA más agresiva"""

    def __init__(self, name="Bot Agresivo"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        import random

        if not available_actions:
            return None

        # IA agresiva - prefiere apostar y subir
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.1  # 10% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.3  # 30% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.5  # 50% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.1  # 10% probabilidad de all-in

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🔥 {self.name}: {description}")


class ConservativeAIStrategy(PlayerStrategy):
    """Estrategia de IA más conservadora"""

    def __init__(self, name="Bot Conservador"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        import random

        if not available_actions:
            return None

        # IA conservadora - prefiere check/call y fold
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.3  # 30% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.6  # 60% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.08  # 8% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.02  # 2% probabilidad de all-in

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🛡️ {self.name}: {description}")


class CardCountingStrategy(PlayerStrategy):
    """Estrategia que cuenta cartas básicamente (simulada)"""

    def __init__(self, name="Contador de Cartas"):
        self.name = name
        self.cards_seen = []

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        if not available_actions:
            return None

        # Simular conteo de cartas básico
        # Analizar las cartas del jugador y las comunitarias
        all_visible_cards = list(player_cards) + list(board_cards)

        # Estrategia basada en número de cartas comunitarias
        num_community = len(board_cards)

        action_weights = []
        for action_type, description, amount in available_actions:
            if action_type == "fold":
                # Más conservador en el pre-flop
                weight = 0.3 if num_community == 0 else 0.15
            elif action_type in ["check", "call"]:
                # Más agresivo con más información
                weight = 0.4 if num_community == 0 else 0.5
            elif action_type in ["bet", "raise"]:
                # Más agresivo en calles tardías
                weight = 0.2 if num_community == 0 else 0.3
            else:  # all-in
                weight = 0.1 if num_community >= 3 else 0.05

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        return selected_action[0], selected_action[2]

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🧠 {self.name} eligió: {description} (basado en análisis)")


class BluffingStrategy(PlayerStrategy):
    """Estrategia que incluye bluffs ocasionales"""

    def __init__(self, name="Bluffer"):
        self.name = name
        self.bluff_frequency = 0.2  # 20% de las veces
        self.last_bluff_round = -1

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        if not available_actions:
            return None

        # Decidir si hacer bluff esta ronda
        # Usamos el número de cartas comunitarias como proxy para la ronda
        current_street = len(board_cards)
        should_bluff = (random.random() < self.bluff_frequency and
                        current_street != self.last_bluff_round)

        if should_bluff:
            self.last_bluff_round = current_street
            # Buscar acción más agresiva disponible
            for action_type, description, amount in reversed(available_actions):
                if action_type in ["bet", "raise"]:
                    return action_type, amount

        # Comportamiento normal - similar a SimpleAI pero más agresivo
        action_weights = []
        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.15
            elif action_type in ["check", "call"]:
                weight = 0.5
            elif action_type in ["bet", "raise"]:
                weight = 0.3
            else:  # all-in
                weight = 0.05

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        return selected_action[0], selected_action[2]

    def on_action_taken(self, player_index, action_type, amount, description):
        if action_type in ["bet", "raise"] and hasattr(self, 'last_bluff_round'):
            if self.last_bluff_round == getattr(self, 'current_street', -1):
                print(f"😈 {self.name} eligió: {description} (¿bluff?)")
            else:
                print(f"💪 {self.name} eligió: {description}")
        else:
            print(f"🎭 {self.name} eligió: {description}")


class DataCollectionStrategy(PlayerStrategy):
    """Estrategia que recolecta datos de la partida para análisis"""

    def __init__(self, name="Analizador", base_strategy=None):
        self.name = name
        self.base_strategy = base_strategy or SimpleAIStrategy("Base")
        self.game_data = {
            'hands_played': 0,
            'actions_taken': [],
            'win_rate': 0,
            'total_winnings': 0
        }

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        # Recopilar datos del estado actual
        self.game_data['hands_played'] += 1

        # Usar la estrategia base para la decisión
        decision = self.base_strategy.make_decision(
            player_cards, board_cards, available_actions)

        # Registrar la decisión
        if decision:
            self.game_data['actions_taken'].append({
                # Usar número de cartas comunitarias como indicador de calle
                'street': len(board_cards),
                'action_type': decision[0],
                'amount': decision[1],
                'num_player_cards': len(player_cards),
                'num_board_cards': len(board_cards)
            })

        return decision

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"📊 {self.name} eligió: {description} [Datos recopilados]")

    def get_statistics(self):
        """Retorna estadísticas recopiladas"""
        return self.game_data.copy()


class SimpleAIStrategy(PlayerStrategy):
    """Estrategia de IA simple con comportamiento aleatorio"""

    def __init__(self, name="Bot"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        """Implementa una IA simple para los jugadores automáticos"""
        import random

        if not available_actions:
            return None

        # IA muy básica - comportamiento aleatorio con algunas tendencias
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.2  # 20% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.6  # 60% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.15  # 15% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.05  # 5% probabilidad de all-in

            action_weights.append(weight)

        # Seleccionar acción basada en probabilidades
        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🤖 {self.name} eligió: {description}")


class AggressiveAIStrategy(PlayerStrategy):
    """Estrategia de IA más agresiva"""

    def __init__(self, name="Bot Agresivo"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        import random

        if not available_actions:
            return None

        # IA agresiva - prefiere apostar y subir
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.1  # 10% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.3  # 30% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.5  # 50% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.1  # 10% probabilidad de all-in

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🔥 {self.name} eligió: {description}")


class ConservativeAIStrategy(PlayerStrategy):
    """Estrategia de IA más conservadora"""

    def __init__(self, name="Bot Conservador"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, player_cards, board_cards, available_actions):
        import random

        if not available_actions:
            return None

        # IA conservadora - prefiere retirarse o igualar
        action_weights = []

        for action_type, description, amount in available_actions:
            if action_type == "fold":
                weight = 0.5  # 50% probabilidad de fold
            elif action_type in ["check", "call"]:
                weight = 0.4  # 40% probabilidad de check/call
            elif action_type in ["bet", "raise"]:
                weight = 0.05  # 5% probabilidad de apostar/subir
            else:  # all-in
                weight = 0.05  # 5% probabilidad de all-in

            action_weights.append(weight)

        selected_action = random.choices(
            available_actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        return action_type, amount

    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🛡️ {self.name} eligió: {description}")
