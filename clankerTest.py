from CLANKER import Clanker
from pokerSimulator import InteractivePokerGame
from example_custom_players import SimpleAIStrategy

# Crear estrategias para los jugadores
strategies = [
    Clanker(),
    SimpleAIStrategy("Bot Simple"),
    SimpleAIStrategy("Bot Simple 2")
]

# Configurar el juego
starting_stacks = [10000, 10000, 10000]
blinds = (50, 100)

# Crear y ejecutar usando el método estático con los parámetros correctos
InteractivePokerGame.repeated_hand_simulation(
    player_strategies=strategies,
    starting_stacks=starting_stacks,
    blinds=blinds
)
