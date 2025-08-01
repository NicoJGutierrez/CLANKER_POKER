
from pokerkit import Automation, Mode, NoLimitTexasHoldem
from abc import ABC, abstractmethod
from deuces import Card
from playerstrategyABC import PlayerStrategy
from example_custom_players import SimpleAIStrategy, AggressiveAIStrategy, ConservativeAIStrategy
import traceback


def convert_pokerkit_to_deuces_cards(pokerkit_cards):
    """
    Convierte cartas de pokerkit a formato deuces para pretty printing
    """
    if not pokerkit_cards:
        return []

    deuces_cards = []
    for card in pokerkit_cards:
        try:
            # Intentar convertir usando la representación string de la carta
            card_str = str(card)

            # Parsear la representación más compleja de pokerkit
            # Ejemplo: "SIX OF DIAMONDS (6d)" -> "6d"
            if '(' in card_str and ')' in card_str:
                # Extraer la parte entre paréntesis
                start = card_str.find('(')
                end = card_str.find(')', start)
                if start != -1 and end != -1:
                    short_form = card_str[start+1:end]

                    # Crear carta deuces
                    if len(short_form) >= 2:
                        try:
                            deuces_card = Card.new(short_form)
                            deuces_cards.append(deuces_card)
                            continue
                        except:
                            pass

            # Fallback: intentar mapeo directo
            suit_map = {'♠': 's', '♥': 'h', '♦': 'd', '♣': 'c'}
            if len(card_str) >= 2:
                rank = card_str[0]
                suit_symbol = card_str[1]

                if suit_symbol in suit_map:
                    deuces_card_str = rank + suit_map[suit_symbol]
                    deuces_card = Card.new(deuces_card_str)
                    deuces_cards.append(deuces_card)
                    continue

            # Último fallback: usar string representation
            deuces_cards.append(card_str)

        except Exception as e:
            # Si falla la conversión, usar string representation
            deuces_cards.append(str(card))

    return deuces_cards


def safe_print_pretty_cards(cards, prefix=""):
    """
    Imprime cartas de manera segura con pretty printing o fallback
    """
    if not cards:
        print(f"{prefix}(Sin cartas)")
        return

    try:
        # Intentar usar deuces para pretty printing
        deuces_cards = convert_pokerkit_to_deuces_cards(cards)

        # Verificar si tenemos cartas válidas para deuces
        valid_deuces_cards = [c for c in deuces_cards if isinstance(c, int)]

        if len(valid_deuces_cards) > 0:
            # Usar pretty printing de deuces
            import io
            import sys

            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()
            Card.print_pretty_cards(valid_deuces_cards)
            cards_output = buffer.getvalue()
            sys.stdout = old_stdout

            # Añadir prefijo a cada línea si hay salida válida
            lines = cards_output.strip().split('\n')
            if lines and any(line.strip() for line in lines):
                for line in lines:
                    if line.strip():
                        print(f"{prefix}{line}")
            else:
                # Fallback si no hay salida válida
                card_strings = []
                for card in cards:
                    card_str = str(card)
                    if '(' in card_str and ')' in card_str:
                        start = card_str.find('(')
                        end = card_str.find(')', start)
                        if start != -1 and end != -1:
                            card_strings.append(card_str[start+1:end])
                        else:
                            card_strings.append(card_str)
                    else:
                        card_strings.append(card_str)
                print(f"{prefix}{' '.join(card_strings)}")
        else:
            # Fallback: usar representación string simple
            card_strings = []
            for card in cards:
                card_str = str(card)
                if '(' in card_str and ')' in card_str:
                    start = card_str.find('(')
                    end = card_str.find(')', start)
                    if start != -1 and end != -1:
                        card_strings.append(card_str[start+1:end])
                    else:
                        card_strings.append(card_str)
                else:
                    card_strings.append(card_str)
            print(f"{prefix}{' '.join(card_strings)}")

    except Exception as e:
        # Fallback final: representación string simple
        card_strings = []
        for card in cards:
            card_str = str(card)
            if '(' in card_str and ')' in card_str:
                start = card_str.find('(')
                end = card_str.find(')', start)
                if start != -1 and end != -1:
                    card_strings.append(card_str[start+1:end])
                else:
                    card_strings.append(card_str)
            else:
                card_strings.append(card_str)
        print(f"{prefix}{' '.join(card_strings)}")


class HumanPlayerStrategy(PlayerStrategy):
    """Estrategia para jugador humano interactivo"""

    def __init__(self, name="Jugador Humano"):
        self.name = name

    def get_name(self):
        return self.name

    def make_decision(self, game_state, available_actions, player_index):
        """Solicita al jugador humano que elija una acción"""
        if not available_actions:
            print("❌ No hay acciones disponibles")
            return None

        print("\n🎮 TUS OPCIONES:")
        print("-" * 30)

        for i, (action_type, description, amount) in enumerate(available_actions, 1):
            print(f"{i}. {description}")

        while True:
            try:
                choice = input(
                    f"\nElige tu acción (1-{len(available_actions)}): ").strip()
                choice_idx = int(choice) - 1

                if 0 <= choice_idx < len(available_actions):
                    action_type, description, default_amount = available_actions[choice_idx]

                    # Si es una apuesta/subida personalizada, permitir ingreso de cantidad
                    if action_type in ["bet", "raise"] and default_amount > 0:
                        min_amount = game_state.min_completion_betting_or_raising_to_amount
                        max_amount = game_state.max_completion_betting_or_raising_to_amount

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

    def on_action_taken(self, player_index, action_type, amount, description):
        # El jugador humano ya ve las acciones, no necesita callback adicional
        pass


class InteractivePokerGame:
    def __init__(self, player_strategies=None, starting_stacks=None, blinds=(200, 400)):
        """
        Inicializa una simulación interactiva de Texas Hold'em No Limit

        Args:
            player_strategies: Lista de estrategias PlayerStrategy para cada jugador
            starting_stacks: Lista con fichas iniciales para cada jugador
            blinds: Tupla con (small blind, big blind)
        """
        # Configuración por defecto si no se proporcionan estrategias
        if player_strategies is None:
            player_strategies = [
                ConservativeAIStrategy("Bot 0"),
                SimpleAIStrategy("Bot 1"),
                SimpleAIStrategy("Bot 2"),
                AggressiveAIStrategy("Bot 3"),
                SimpleAIStrategy("Bot 4"),
            ]

        self.player_strategies = player_strategies
        num_players = len(player_strategies)

        if starting_stacks is None:
            starting_stacks = [10000] * num_players

        self.player_names = [strategy.get_name()
                             for strategy in player_strategies]

        # Encontrar el índice del jugador humano (si existe)
        self.human_player = -1
        for i, strategy in enumerate(player_strategies):
            if isinstance(strategy, HumanPlayerStrategy):
                self.human_player = i
                break

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
            len(player_strategies),  # Number of players
            mode=Mode.TOURNAMENT,
        )

    def print_game_state(self, show_all_cards=False, compact=False):
        """Imprime el estado actual del juego"""
        if compact:
            # Versión compacta para turnos entre acciones
            street_names = ["Pre-flop", "Flop", "Turn", "River"]
            try:
                current_street = street_names[min(
                    self.state.street_index if self.state.street_index is not None else 0, 3)]
            except (TypeError, AttributeError):
                current_street = "Pre-flop"

            total_pot = sum(self.state.bets) if self.state.bets else 0

            # Cartas comunitarias con pretty printing
            community_cards = []
            try:
                for cards in self.state.board_cards:
                    community_cards.extend(cards)
            except (TypeError, AttributeError):
                pass

            print(f"\n{current_street} | Bote: {total_pot:,}")
            if community_cards:
                print("🃏 Mesa:")
                safe_print_pretty_cards(community_cards)
            else:
                print("🃏 Mesa: (Sin cartas)")

            # Información compacta de jugadores
            for i in range(self.state.player_count):
                name = self.player_names[i]
                stack = self.state.stacks[i]
                bet = self.state.bets[i] if self.state.bets else 0

                # Indicador de turno
                turn_indicator = "👉" if (
                    self.state.actor_indices and i == self.state.actor_indices[0]) else "  "

                # Cartas del jugador - mostrar para todos si no hay jugador humano, o según condiciones
                should_show_cards = (show_all_cards or
                                     # No hay jugador humano, mostrar todas
                                     (self.human_player < 0) or
                                     # Es el jugador humano
                                     (i == self.human_player))

                if should_show_cards:
                    if self.state.hole_cards[i]:
                        print(
                            f"{turn_indicator} {name}: {stack:,} (apuesta: {bet:,})")
                        safe_print_pretty_cards(
                            self.state.hole_cards[i], "       ")
                    else:
                        print(
                            f"{turn_indicator} {name}: {stack:,} (apuesta: {bet:,}) [Fold]")
                else:
                    print(f"{turn_indicator} {name}: {stack:,} (apuesta: {bet:,})")
        else:
            # Versión completa original
            print("\n" + "="*60)
            print("🎰 LETS GO GAMBLING!!! 🎰")
            print("="*60)

            # Pot total
            total_pot = sum(self.state.bets) if self.state.bets else 0

            # Información de jugadores
            print("\n👥 JUGADORES:")
            print("-" * 50)

            for i in range(self.state.player_count):
                name = self.player_names[i]
                status = "✅ Activo" if self.state.statuses[i] else "❌ Fuera"
                stack = self.state.stacks[i]
                bet = self.state.bets[i] if self.state.bets else 0

                # Cartas del jugador - mostrar para todos si no hay jugador humano, o según condiciones
                should_show_cards = (show_all_cards or
                                     # No hay jugador humano, mostrar todas
                                     (self.human_player < 0) or
                                     # Es el jugador humano
                                     (i == self.human_player))

                # Indicador de turno
                turn_indicator = "👉" if (
                    self.state.actor_indices and i == self.state.actor_indices[0]) else "  "

                print(f"{turn_indicator} {name}:")
                print(f"     Estado: {status}")
                print(f"     Stack: {stack:,}")
                print(f"     Apuesta: {bet:,}")

                if should_show_cards:
                    if self.state.hole_cards[i]:
                        safe_print_pretty_cards(
                            self.state.hole_cards[i], "       ")
                    else:
                        print(f"     Sin cartas")
                else:
                    print(
                        f"     🂠 🂠" if self.state.hole_cards[i] else "     Sin cartas")
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

    def get_player_action(self, player_index):
        """Obtiene la acción de un jugador usando su estrategia"""
        actions = self.get_available_actions()
        if not actions:
            return None

        strategy = self.player_strategies[player_index]
        return strategy.make_decision(self.state, actions, player_index)

    def get_human_action(self):
        """Método legacy - ahora redirige a get_player_action"""
        if self.human_player >= 0:
            return self.get_player_action(self.human_player)
        return None

    def get_ai_action(self, player_idx):
        """Método legacy - ahora redirige a get_player_action"""
        return self.get_player_action(player_idx)

    def execute_action(self, action_type, amount, player_index=None):
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

            # Notificar a la estrategia sobre la acción tomada
            if player_index is not None and 0 <= player_index < len(self.player_strategies):
                strategy = self.player_strategies[player_index]
                actions = self.get_available_actions()
                description = next(
                    (desc for act, desc, amt in actions if act == action_type), action_type)
                strategy.on_action_taken(
                    player_index, action_type, amount, description)

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
        print("RESULTADOS FINALES 🏆")

        try:
            # Mostrar siempre todas las cartas en los resultados finales
            self.print_game_state(show_all_cards=True)

            # Mostrar ganadores
            active_players = [i for i, status in enumerate(
                self.state.statuses) if status]
            if len(active_players) == 1:
                winner = active_players[0]
                print(
                    f"🥇 {self.player_names[winner]} gana por ser el único jugador restante!")
            elif len(active_players) > 1:
                print(
                    f"🎪 A {len(active_players)} jugadores les toca mostrar sus cartas")

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

        # Mostrar información especial para heads-up (2 jugadores)
        if self.state.player_count == 2:
            print("⚔️ ¡HEADS-UP! Solo quedan 2 jugadores")

        if self.human_player >= 0 and self.human_player < len(self.player_names):
            print(f"🎯 Tú eres {self.player_names[self.human_player]}")

        self.print_game_state()  # Estado inicial completo

        # Contador de seguridad para evitar bucles infinitos
        max_actions = 1000
        action_count = 0

        # Loop principal del juego
        try:
            while not self.is_hand_over() and action_count < max_actions:
                if not self.state.actor_indices:
                    break

                current_player = self.state.actor_indices[0]

                # Obtener acción del jugador actual usando su estrategia
                action = self.get_player_action(current_player)
                if action is None:
                    break

                action_type, amount = action
                if not self.execute_action(action_type, amount, current_player):
                    continue

                action_count += 1

                # Mostrar estado actualizado en formato compacto
                self.print_game_state(compact=True)

            if action_count >= max_actions:
                print(
                    "⚠️ Se alcanzó el límite máximo de acciones. Terminando la mano...")

        except Exception as e:
            print(f"⚠️ Error durante el juego: {e}")
            print("Terminando la mano...")

        # Mostrar resultados
        self.show_results()

    @staticmethod
    def repeated_hand_simulation(player_strategies=None, starting_stacks=None, blinds=(50, 100)):
        """Función principal para ejecutar la simulación"""

        # Configuración por defecto si no se proporcionan estrategias
        if player_strategies is None:
            player_strategies = [
                SimpleAIStrategy("SimpleBot 1"),
                AggressiveAIStrategy("AggressiveBot"),
                ConservativeAIStrategy("ConservativeBot"),
                SimpleAIStrategy("SimpleBot 2"),
                SimpleAIStrategy("SimpleBot 3")
            ]

        # Configuración por defecto para stacks
        if starting_stacks is None:
            starting_stacks = [10000] * len(player_strategies)
        print("🎰" * 20)
        print("No Limit Texas Hold'em!")
        print("🎰" * 20)
        try:
            # Crear y ejecutar el juego
            game = InteractivePokerGame(
                starting_stacks=starting_stacks,
                blinds=blinds,
                player_strategies=player_strategies
            )

            game.play_hand()

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
                            f"🎮 Continúa con {len(active_players)} jugadores")

                        # Crear nuevas estrategias para los jugadores activos
                        active_strategies = [game.player_strategies[i]
                                             for i in active_players]

                        game = InteractivePokerGame(
                            player_strategies=active_strategies,
                            starting_stacks=adjusted_stacks,
                            blinds=blinds
                        )

                        game.play_hand()
                    else:

                        print("🏁 Solo queda un jugador. ¡Juego terminado!")
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

                                f"🏆 ¡{winner_name} gana el torneo con {new_stacks[winner_idx]:,} fichas!")
                        else:
                            print("🚫 Error: No se pudo determinar el ganador")
                        break
                    else:

                        print("🚫 No hay suficientes jugadores para continuar")
                        break

        except KeyboardInterrupt:
            print("\n👋 Juego cancelado. ¡Hasta la próxima!")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
            print("Línea del error:")
            traceback.print_exc()


if __name__ == "__main__":
    InteractivePokerGame.repeated_hand_simulation()
