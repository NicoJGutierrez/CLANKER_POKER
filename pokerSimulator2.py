import datetime
from pokerkit import Automation, Mode, NoLimitTexasHoldem
from playerstrategyABC import PlayerStrategy


class GameLogger:
    # Esta clase se usa para imprimir elementos en consola y guardarlos en un archivo log.txt con metadatos asociados
    def __init__(self):
        self.filename = "log" + datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + ".txt"
        self.printing_enabled = True
        self.logging_enabled = True
        self.log("Game started at " +
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def log(self, message):
        if self.printing_enabled:
            print(message)
        if self.logging_enabled:
            with open(self.filename, 'a') as f:
                f.write(f"{message}\n")

    def close(self):
        self.log("Game ended at " +
                 datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        if self.logging_enabled:
            with open(self.filename, 'a') as f:
                f.write("\n\n")


class PokerSimulatorGame:
    def __init__(self, player_strategies=None, starting_stacks=None, blinds=(200, 400)):
        self.player_strategies = player_strategies or []
        self.starting_stacks = starting_stacks or [
            10000] * len(self.player_strategies)
        self.blinds = blinds
        self.game_log = GameLogger()
        self.player_names = [strategy.get_name()
                             for strategy in player_strategies]

        self.state = NoLimitTexasHoldem.create_state(
            # Automatizamos todo excepto las decisiones de juego
            (
                Automation.ANTE_POSTING,
                Automation.BET_COLLECTION,
                Automation.BLIND_OR_STRADDLE_POSTING,
                Automation.CARD_BURNING,
                Automation.HOLE_DEALING,
                Automation.BOARD_DEALING,
                Automation.HOLE_CARDS_SHOWING_OR_MUCKING,
                Automation.HAND_KILLING,
                Automation.CHIPS_PUSHING,
                Automation.CHIPS_PULLING,
            ),
            False,  # Uniform antes?
            0,  # Antes
            blinds,  # Blinds
            blinds[1],  # Min-bet (igual al big blind)
            tuple(starting_stacks),  # Starting stacks
            len(player_strategies),  # Number of players
            mode=Mode.TOURNAMENT,
        )

    def get_actions(self):
        actions = []
        current_player = self.state.actor_indices[0]
        current_bet = max(self.state.bets) if self.state.bets else 0
        player_bet = self.state.bets[current_player]
        to_call = current_bet - player_bet

        if self.state.can_fold():
            actions.append(("fold", "Retirarse", 0))

        # Verificar si puede hacer check/call
        if self.state.can_check_or_call():
            if to_call == 0:
                actions.append(("check", "Pasar", 0))
            else:
                actions.append(("call", f"Igualar ({to_call:,})", to_call))

        # Verificar si puede apostar/subir
        if self.state.can_complete_bet_or_raise_to():
            min_raise = self.state.min_completion_betting_or_raising_to_amount
            max_raise = self.state.max_completion_betting_or_raising_to_amount

            if min_raise is not None and max_raise is not None:
                if current_bet == 0:
                    actions.append(
                        ("bet", f"Apostar (min: {min_raise:,})", min_raise))
                else:
                    actions.append(
                        ("raise", f"Subir (min: {min_raise:,})", min_raise))

                # All-in si es diferente del máximo
                if max_raise > min_raise:
                    actions.append(
                        ("allin", f"All-in ({max_raise:,})", max_raise))

        return actions

    def get_player_action(self, player_index):
        # Obtiene la acción de un jugador usando su estrategia

        actions = self.get_actions()
        if not actions:
            return None

        community_cards = []
        try:
            for cards in self.state.board_cards:
                community_cards.extend(cards)
        except (TypeError, AttributeError):
            pass

        strategy = self.player_strategies[player_index]
        return strategy.make_decision(self.state.hole_cards[player_index], community_cards, actions)

    def execute_player_action(self, player_index, action_type, amount):
        if action_type is None:
            raise ValueError(
                f"No action provided by strategy {self.player_names[player_index]} (player {player_index})")

        # Ejecutar la acción
        if action_type == "fold":
            self.state.fold()
        elif action_type == "check":
            self.state.check_or_call()
        elif action_type == "call":
            self.state.check_or_call()
        elif action_type in ["bet", "raise", "allin"]:
            self.state.complete_bet_or_raise_to(amount)

        self.game_log.log(
            f"Player {self.player_names[player_index]} ({player_index}) - Action: {action_type} Amount: {amount}")

    def show_results(self, num_mano):
        """Muestra los resultados finales de la mano"""
        self.game_log.log(f"RESULTADOS MANO {num_mano} 🏆")

        # Mostrar siempre todas las cartas en los resultados finales
        self.print_game_state(show_all_cards=True)

        # Mostrar ganadores
        active_players = [i for i, status in enumerate(
            self.state.statuses) if status]
        if len(active_players) == 1:
            winner = active_players[0]
            self.game_log.log(
                f"{self.player_names[winner]} gana por ser el único jugador restante!")
        elif len(active_players) > 1:
            self.game_log.log(
                f"A {len(active_players)} jugadores les toca mostrar sus cartas")

        # Mostrar stacks finales
        self.game_log.log("\n💰 FICHAS FINALES:")
        eliminated_players = []
        for i, (name, stack) in enumerate(zip(self.player_names, self.state.stacks)):
            self.game_log.log(f"   {name}: {stack:,}")
            if stack == 0:
                eliminated_players.append(name)

        # Mostrar jugadores eliminados
        if eliminated_players:
            self.game_log.log(
                f"\nJUGADORES ELIMINADOS: {', '.join(eliminated_players)}")

    def play_hand(self):
        """Juega una mano completa"""

        # Mostrar información especial para heads-up (2 jugadores)
        if self.state.player_count == 2:
            self.game_log.log("¡HEADS-UP! Quedan 2 jugadores")
        for i in range(self.state.player_count):
            name = self.player_names[i]
            stack = self.state.stacks[i]
            if self.state.hole_cards[i]:
                self.game_log.log(
                    f"{name}: {stack:,} - Cards: {self.state.hole_cards[i]}")

        # La mano termina cuando la calle actual es none
        current_street = 0
        while self.state.street_index is not None:

            current_player = self.state.actor_indices[0]

            # Si hay una nueva carta en la mesa mostramos las cartas en la mesa
            if self.state.street_index > current_street:
                current_street = self.state.street_index
                self.game_log.log(
                    f"Cartas en la mesa: {self.state.board_cards}")

            # Obtener acción del jugador actual usando su estrategia
            action = self.get_player_action(current_player)
            if action is None:
                break

            action_type, amount = action
            self.execute_player_action(
                current_player, action_type=action_type, amount=amount)

    def repeated_hand_simulation(self, player_strategies: list[PlayerStrategy], starting_stacks=list[int], blinds=(50, 100)):
        if len(player_strategies) != len(starting_stacks):
            raise ValueError(
                "El número de estrategias debe coincidir con el número de stacks iniciales")

        # Loggear metadatos iniciales
        metadata = f"""Número de jugadores: {len(player_strategies)}
                    Stacks iniciales: {starting_stacks}
                    Blinds: Small Blind = {blinds[0]:,}, Big Blind = {blinds[1]:,}
                    Estrategias:"""

        for i, strategy in enumerate(player_strategies):
            metadata += f"\n  {i+1}. {strategy.get_name()} ({strategy.__class__.__name__})"

        self.game_log.log(metadata)

        while self.state.player_count > 1:
            self.play_hand()

        self.game_log.log(
            f"El juego ha terminado, ganador final: {self.player_names[0]} con {self.state.stacks[0]:,} fichas")
