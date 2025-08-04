from deuces import Evaluator
from playerstrategyABC import PlayerStrategy


class Clanker(PlayerStrategy):

    def __init__(self):
        super().__init__()
        self.equityVar = 0.0

    def get_name(self):
        return "Clanker"

    def equity(self, mano, cartas_en_mesa):
        evaluator = Evaluator()
        self.equityVar = 1 - \
            ((1 - evaluator.evaluate(mano, cartas_en_mesa))/7462)
        return self.equityVar

    def make_decision(self, player_cards, board_cards, available_actions):
        # Nota: Esta implementación necesita ser adaptada ya que no tenemos
        # acceso directo al estado completo del juego (num_players, pot, chips)
        # Para una implementación completa, sería mejor pasar esta información
        # como parte de available_actions o crear un método auxiliar

        if not player_cards:
            return ("fold", 0) if any(action[0] == "fold" for action in available_actions) else available_actions[0][:2]

        # Evaluación de equity usando deuces
        evaluator = Evaluator()
        if board_cards:
            try:
                hand_strength = evaluator.evaluate(player_cards, board_cards)
                # Normalizar el valor (más bajo es mejor en deuces, convertir a equity)
                EV = 1 - ((hand_strength - 1) / 7461)
            except:
                EV = 0.5  # Valor neutral si falla la evaluación
        else:
            # Pre-flop: evaluación simple basada en las cartas del jugador
            EV = 0.5  # Valor neutral para pre-flop

        # Buscar si hay una acción de bet/raise disponible
        bet_available = any(action[0] in ["bet", "raise"]
                            for action in available_actions)

        # Implementación de la lógica para elegir la jugada
        if bet_available:
            if EV > 0.8:
                # All-in si está disponible, sino la apuesta más alta
                for action_type, _, amount in reversed(available_actions):
                    if action_type in ["bet", "raise", "allin"]:
                        return action_type, amount
            elif EV > 0.6:
                # Apuesta moderada
                for action_type, _, amount in available_actions:
                    if action_type in ["bet", "raise"]:
                        return action_type, amount
            elif EV > 0.4:
                # Call si está disponible
                for action_type, _, amount in available_actions:
                    if action_type in ["call", "check"]:
                        return action_type, amount
            else:
                return "fold", 0
        else:
            if EV > 0.6:
                # Check/call
                for action_type, _, amount in available_actions:
                    if action_type in ["check", "call"]:
                        return action_type, amount
            else:
                return "fold", 0

        # Fallback: tomar la primera acción disponible
        return available_actions[0][0], available_actions[0][2]

    def on_action_taken(self, player_index, action_type, amount, description):
        """
        Callback cuando se toma una acción (para logging, análisis, etc.)
        Aquí se puede implementar el registro de acciones o cualquier otra lógica necesaria.
        """
        print(
            f"Jugador {player_index} tomó la acción: {action_type} de {amount} fichas. Descripción: {description}, Equity: {self.equityVar:.2f}")
