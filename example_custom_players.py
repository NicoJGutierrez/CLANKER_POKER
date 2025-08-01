"""
Ejemplo de cómo crear jugadores personalizados para el simulador de poker
"""

from pokerSimulator import (
    PlayerStrategy,
    InteractivePokerGame,
    HumanPlayerStrategy,
    SimpleAIStrategy,
    AggressiveAIStrategy,
    ConservativeAIStrategy
)
import random


class CardCountingStrategy(PlayerStrategy):
    """Estrategia que cuenta cartas básicamente (simulada)"""

    def __init__(self, name="Contador de Cartas"):
        self.name = name
        self.cards_seen = []

    def get_name(self):
        return self.name

    def make_decision(self, game_state, available_actions, player_index):
        if not available_actions:
            return None

        # Simular conteo de cartas básico
        # En una implementación real, analizaríamos las cartas comunitarias
        # y ajustaríamos las probabilidades

        # Obtener información del estado
        community_cards = []
        try:
            for cards in game_state.board_cards:
                community_cards.extend(cards)
        except (TypeError, AttributeError):
            pass

        # Estrategia basada en número de cartas comunitarias
        num_community = len(community_cards)

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

    def make_decision(self, game_state, available_actions, player_index):
        if not available_actions:
            return None

        # Decidir si hacer bluff esta ronda
        should_bluff = (random.random() < self.bluff_frequency and
                        game_state.street_index != self.last_bluff_round)

        if should_bluff:
            self.last_bluff_round = game_state.street_index
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

    def make_decision(self, game_state, available_actions, player_index):
        # Recopilar datos del estado actual
        self.game_data['hands_played'] += 1

        # Usar la estrategia base para la decisión
        decision = self.base_strategy.make_decision(
            game_state, available_actions, player_index)

        # Registrar la decisión
        if decision:
            self.game_data['actions_taken'].append({
                'street': game_state.street_index,
                'action_type': decision[0],
                'amount': decision[1],
                'pot_size': sum(game_state.bets) if game_state.bets else 0
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

    def make_decision(self, game_state, available_actions, player_index):
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

    def make_decision(self, game_state, available_actions, player_index):
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

    def make_decision(self, game_state, available_actions, player_index):
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

def example_custom_game():
    """Ejemplo de juego con jugadores personalizados"""
    print("🎯 Iniciando juego con estrategias personalizadas")

    # Crear diferentes tipos de jugadores
    strategies = [
        HumanPlayerStrategy("Jugador Humano"),
        CardCountingStrategy("Contador"),
        BluffingStrategy("El Bluffer"),
        DataCollectionStrategy(
            "Analizador", ConservativeAIStrategy("Base Conservador"))
    ]

    starting_stacks = [10000, 10000, 10000, 10000]
    blinds = (50, 100)

    game = InteractivePokerGame(
        player_strategies=strategies,
        starting_stacks=starting_stacks,
        blinds=blinds
    )

    game.play_hand()

    # Mostrar estadísticas del analizador si existe
    for i, strategy in enumerate(game.player_strategies):
        if isinstance(strategy, DataCollectionStrategy):
            stats = strategy.get_statistics()
            print(f"\n📈 Estadísticas de {strategy.get_name()}:")
            print(f"   Manos jugadas: {stats['hands_played']}")
            print(f"   Acciones tomadas: {len(stats['actions_taken'])}")


def example_ai_only_game():
    """Ejemplo de juego solo entre IAs"""
    print("🤖 Iniciando juego solo entre IAs")

    strategies = [
        AggressiveAIStrategy("Agresivo 1"),
        ConservativeAIStrategy("Conservador 1"),
        BluffingStrategy("Bluffer 1"),
        CardCountingStrategy("Contador 1"),
        SimpleAIStrategy("Simple 1")
    ]

    starting_stacks = [5000] * 5
    blinds = (25, 50)

    game = InteractivePokerGame(
        player_strategies=strategies,
        starting_stacks=starting_stacks,
        blinds=blinds
    )

    game.play_hand()


if __name__ == "__main__":
    print("Selecciona el tipo de juego:")
    print("1. Juego con jugadores personalizados (incluye humano)")
    print("2. Juego solo entre IAs")

    choice = input("Elige opción (1 o 2): ").strip()

    if choice == "1":
        example_custom_game()
    elif choice == "2":
        example_ai_only_game()
    else:
        print("⚠️ Opción inválida, ejecutando juego por defecto")
        example_custom_game()
