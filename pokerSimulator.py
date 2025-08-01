from math import inf
from pokerkit import Automation, Mode, NoLimitTexasHoldem


class InteractivePokerGame:
    def __init__(self, num_players=3, starting_stacks=None, blinds=(200, 400)):
        """
        Inicializa una simulación interactiva de Texas Hold'em No Limit

        Args:
            num_players: Número de jugadores (por defecto 3)
            starting_stacks: Lista con fichas iniciales para cada jugador
            blinds: Tupla con (small blind, big blind)
        """
        if starting_stacks is None:
            starting_stacks = [10000] * num_players

        self.player_names = [f"Jugador {i+1}" for i in range(num_players)]
        self.human_player = 0  # El jugador humano es el índice 0

        # Crear el estado del juego
        self.state = NoLimitTexasHoldem.create_state(
            # Automations - automatizamos todo excepto las decisiones de juego
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
            0,  # Antes (sin antes en este juego)
            blinds,  # Blinds
            blinds[1],  # Min-bet (igual al big blind)
            tuple(starting_stacks),  # Starting stacks
            num_players,  # Number of players
            mode=Mode.TOURNAMENT,
        )

    def print_game_state(self, show_all_cards=False):
        """Imprime el estado actual del juego"""
        print("\n" + "="*60)
        print("🎰 ESTADO ACTUAL DEL JUEGO 🎰")
        print("="*60)

        # Información de la ronda
        street_names = ["Pre-flop", "Flop", "Turn", "River"]
        try:
            current_street = street_names[min(
                self.state.street_index if self.state.street_index is not None else 0, 3)]
        except (TypeError, AttributeError):
            current_street = "Pre-flop"
        print(f"📍 Calle actual: {current_street}")

        # Pot total
        total_pot = sum(self.state.bets) if self.state.bets else 0
        print(f"💰 Bote total: {total_pot}")

        # Cartas comunitarias
        print("\n🃏 CARTAS COMUNITARIAS:")
        community_cards = []
        try:
            for cards in self.state.board_cards:
                community_cards.extend(str(card) for card in cards)
        except (TypeError, AttributeError):
            pass

        if community_cards:
            print(f"   {' '.join(community_cards)}")
        else:
            print("   (Sin cartas aún)")

        # Información de jugadores
        print("\n👥 JUGADORES:")
        print("-" * 50)

        for i in range(self.state.player_count):
            name = self.player_names[i]
            status = "✅ Activo" if self.state.statuses[i] else "❌ Fuera"
            stack = self.state.stacks[i]
            bet = self.state.bets[i] if self.state.bets else 0

            # Cartas del jugador
            if (i == self.human_player and self.human_player >= 0) or show_all_cards:
                if self.state.hole_cards[i]:
                    hole_cards = ' '.join(str(card)
                                          for card in self.state.hole_cards[i])
                else:
                    hole_cards = "Sin cartas"
            else:
                hole_cards = "🂠 🂠" if self.state.hole_cards[i] else "Sin cartas"

            # Indicador de turno
            turn_indicator = "👉" if (
                self.state.actor_indices and i == self.state.actor_indices[0]) else "  "

            print(f"{turn_indicator} {name}:")
            print(f"     Estado: {status}")
            print(f"     Stack: {stack:,}")
            print(f"     Apuesta: {bet:,}")
            print(f"     Cartas: {hole_cards}")
            print()

        # Jugador en turno
        if self.state.actor_indices:
            current_player = self.state.actor_indices[0]
            print(f"🎯 Turno de: {self.player_names[current_player]}")
        else:
            print("🏁 Ronda terminada")

    def get_available_actions(self):
        """Obtiene las acciones disponibles para el jugador actual"""
        if not self.state.actor_indices:
            return []

        actions = []
        current_player = self.state.actor_indices[0]
        current_bet = max(self.state.bets) if self.state.bets else 0
        player_bet = self.state.bets[current_player]
        to_call = current_bet - player_bet

        # Verificar si puede hacer fold
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

    def get_human_action(self):
        """Solicita al jugador humano que elija una acción"""
        actions = self.get_available_actions()

        if not actions:
            print("❌ No hay acciones disponibles")
            return None

        print("\n🎮 TUS OPCIONES:")
        print("-" * 30)

        for i, (action_type, description, amount) in enumerate(actions, 1):
            print(f"{i}. {description}")

        while True:
            try:
                choice = input(
                    f"\nElige tu acción (1-{len(actions)}): ").strip()
                choice_idx = int(choice) - 1

                if 0 <= choice_idx < len(actions):
                    action_type, description, default_amount = actions[choice_idx]

                    # Si es una apuesta/subida personalizada, permitir ingreso de cantidad
                    if action_type in ["bet", "raise"] and default_amount > 0:
                        min_amount = self.state.min_completion_betting_or_raising_to_amount
                        max_amount = self.state.max_completion_betting_or_raising_to_amount

                        custom = input(
                            f"¿Cantidad personalizada? (Enter para mínimo {min_amount:,}): ").strip()
                        if custom:
                            try:
                                amount = int(custom)
                                if min_amount <= amount <= max_amount:
                                    return action_type, amount
                                else:
                                    print(
                                        f"❌ Cantidad debe estar entre {min_amount:,} y {max_amount:,}")
                                    continue
                            except ValueError:
                                print("❌ Ingresa un número válido")
                                continue

                    return action_type, default_amount
                else:
                    print("❌ Opción inválida")
            except ValueError:
                print("❌ Ingresa un número válido")
            except KeyboardInterrupt:
                print("\n👋 Juego cancelado")
                return None

    def get_ai_action(self, player_idx):
        """Implementa una IA simple para los jugadores automáticos"""
        import random

        actions = self.get_available_actions()
        if not actions:
            return None

        # IA muy básica - comportamiento aleatorio con algunas tendencias
        action_weights = []

        for action_type, description, amount in actions:
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
        selected_action = random.choices(actions, weights=action_weights)[0]
        action_type, description, amount = selected_action

        print(f"🤖 {self.player_names[player_idx]} eligió: {description}")

        return action_type, amount

    def execute_action(self, action_type, amount):
        """Ejecuta la acción elegida"""
        try:
            if action_type == "fold":
                self.state.fold()
            elif action_type == "check":
                self.state.check_or_call()
            elif action_type == "call":
                self.state.check_or_call()
            elif action_type in ["bet", "raise", "allin"]:
                self.state.complete_bet_or_raise_to(amount)

            return True
        except Exception as e:
            print(f"❌ Error ejecutando acción: {e}")
            return False

    def is_hand_over(self):
        """Verifica si la mano ha terminado"""
        # Verificar si solo queda un jugador activo
        active_players = sum(1 for status in self.state.statuses if status)
        if active_players <= 1:
            return True

        # Verificar si llegamos al showdown (river completado)
        if self.state.street_index is not None and self.state.street_index >= 4:
            return True

        # Verificar si no hay más acciones pendientes
        if not self.state.actor_indices:
            return True

        # Verificar si el estado indica que la mano ha terminado
        try:
            # Si no podemos obtener acciones válidas, la mano probablemente ha terminado
            if not hasattr(self.state, 'can_fold') or not hasattr(self.state, 'can_check_or_call'):
                return True
        except:
            return True

        return False

    def show_results(self):
        """Muestra los resultados finales de la mano"""
        print("\n" + "🏆" * 20)
        print("RESULTADOS FINALES")
        print("🏆" * 20)

        try:
            self.print_game_state(show_all_cards=True)

            # Mostrar ganadores
            active_players = [i for i, status in enumerate(
                self.state.statuses) if status]
            if len(active_players) == 1:
                winner = active_players[0]
                print(
                    f"\n🥇 {self.player_names[winner]} gana por ser el único jugador restante!")
            elif len(active_players) > 1:
                print(f"\n🎪 Showdown entre {len(active_players)} jugadores")

            # Mostrar stacks finales
            print("\n💰 FICHAS FINALES:")
            eliminated_players = []
            for i, (name, stack) in enumerate(zip(self.player_names, self.state.stacks)):
                print(f"   {name}: {stack:,}")
                if stack == 0:
                    eliminated_players.append(name)

            # Mostrar jugadores eliminados
            if eliminated_players:
                print(
                    f"\n💀 JUGADORES ELIMINADOS: {', '.join(eliminated_players)}")

        except Exception as e:
            print(f"⚠️ Error mostrando resultados: {e}")
            print("La mano ha terminado.")

    def play_hand(self):
        """Juega una mano completa"""
        print("\n🎲 ¡Nueva mano de Texas Hold'em!")

        # Mostrar información especial para heads-up (2 jugadores)
        if self.state.player_count == 2:
            print("⚔️ ¡HEADS-UP! Solo quedan 2 jugadores")

        if self.human_player >= 0 and self.human_player < len(self.player_names):
            print(f"🎯 Tú eres {self.player_names[self.human_player]}")
        else:
            print("🤖 Observando partida entre bots...")

        self.print_game_state()

        # Loop principal del juego
        try:
            while not self.is_hand_over():
                if not self.state.actor_indices:
                    break

                current_player = self.state.actor_indices[0]

                if current_player == self.human_player and self.human_player >= 0:
                    # Turno del jugador humano
                    action = self.get_human_action()
                    if action is None:
                        break

                    action_type, amount = action
                    if not self.execute_action(action_type, amount):
                        continue
                else:
                    # Turno de la IA (o jugador humano eliminado)
                    action = self.get_ai_action(current_player)
                    if action is None:
                        break

                    action_type, amount = action
                    if not self.execute_action(action_type, amount):
                        continue

                    # Pequeña pausa para que sea más natural (más larga si es solo entre bots)
                    import time
                    if self.human_player < 0:
                        time.sleep(2)  # Pausa más larga para observar mejor la partida entre bots
                    else:
                        time.sleep(1)

                # Mostrar estado actualizado
                self.print_game_state()

        except Exception as e:
            print(f"⚠️ Error durante el juego: {e}")
            print("Terminando la mano...")

        # Mostrar resultados
        self.show_results()


def main():
    """Función principal para ejecutar la simulación"""
    print("🎰" * 20)
    print("¡Bienvenido al Texas Hold'em No Limit!")
    print("Vas a jugar contra 2 oponentes controlados por IA")

    try:
        # Configuración del juego
        starting_stacks = [10000, 10000, 10000]  # Fichas iniciales iguales
        blinds = (50, 100)  # Small blind, Big blind

        # Crear y ejecutar el juego
        game = InteractivePokerGame(
            num_players=3,
            starting_stacks=starting_stacks,
            blinds=blinds
        )

        game.play_hand()

        # Preguntar si quiere jugar otra mano
        while True:
            # Crear nuevo juego con stacks actualizados
            new_stacks = list(game.state.stacks)

            # Contar jugadores con fichas suficientes para al menos el small blind
            players_with_chips = sum(
                1 for stack in new_stacks if stack >= blinds[0])

            if players_with_chips >= 2:  # Necesitamos al menos 2 jugadores
                # Ajustar los stacks - si un jugador tiene menos que el big blind pero más que 0,
                # aún puede jugar (podrá hacer all-in)
                adjusted_stacks = []
                active_players = []

                for i, stack in enumerate(new_stacks):
                    if stack > 0:  # Jugador tiene alguna ficha
                        adjusted_stacks.append(stack)
                        active_players.append(i)
                    else:
                        # Jugador eliminado - no incluir en próxima mano
                        continue

                if len(active_players) >= 2:
                    print(
                        f"\n🎮 Continuando con {len(active_players)} jugadores activos")

                    # Actualizar nombres de jugadores para reflejar solo los activos
                    active_names = [game.player_names[i]
                                    for i in active_players]

                    game = InteractivePokerGame(
                        num_players=len(active_players),
                        starting_stacks=adjusted_stacks,
                        blinds=blinds
                    )

                    # Actualizar los nombres para mantener la continuidad
                    game.player_names = active_names

                    # Mantener al humano como jugador 0 si sigue activo
                    if 0 in active_players:
                        game.human_player = active_players.index(0)
                    else:
                        # El jugador humano fue eliminado, pero el juego continúa entre bots
                        print("⚠️ Has sido eliminado del juego")
                        print("🤖 El juego continúa automáticamente entre los bots restantes...")
                        game.human_player = -1  # Indica que no hay jugador humano activo

                    game.play_hand()
                else:
                    print("🚫 Solo queda un jugador con fichas. ¡Juego terminado!")
                    break
            else:
                if players_with_chips == 1:
                    # Encontrar el único jugador restante con fichas
                    winner_idx = None
                    for i, stack in enumerate(new_stacks):
                        if stack > 0:
                            winner_idx = i
                            break

                    if winner_idx is not None:
                        winner_name = game.player_names[winner_idx]
                        print(
                            f"🏆 ¡FELICIDADES! {winner_name} ha ganado el torneo con {new_stacks[winner_idx]:,} fichas!")
                    else:
                        print("🚫 Error: No se pudo determinar el ganador")
                    break
                else:
                    print("🚫 No hay suficientes jugadores con fichas para continuar")
                    break

    except KeyboardInterrupt:
        print("\n👋 Juego cancelado. ¡Hasta la próxima!")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")


if __name__ == "__main__":
    main()
