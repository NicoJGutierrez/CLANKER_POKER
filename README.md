# Simulador de Poker Texas Hold'em - Jugadores Personalizables

Este simulador de poker ha sido refactorizado para permitir el uso de jugadores personalizables mediante una arquitectura de estrategias pluggable.

## 🎯 Características Principales

- **Jugadores Personalizables**: Crea tus propias estrategias de IA
- **Múltiples Estrategias Incluidas**: Humano, IA Simple, Agresiva, Conservadora
- **Interfaz Extensible**: Fácil de extender con nuevos comportamientos
- **Recolección de Datos**: Posibilidad de analizar y registrar partidas
- **Partidas Flexibles**: Desde 2 hasta múltiples jugadores

## 🏗️ Arquitectura

### Clase Base: `PlayerStrategy`

Todas las estrategias de jugadores deben heredar de esta clase abstracta:

```python
from abc import ABC, abstractmethod

class PlayerStrategy(ABC):
    @abstractmethod
    def get_name(self):
        """Retorna el nombre del jugador"""
        pass
    
    @abstractmethod
    def make_decision(self, game_state, available_actions, player_index):
        """Toma una decisión basada en el estado del juego"""
        pass
    
    @abstractmethod
    def on_action_taken(self, player_index, action_type, amount, description):
        """Callback cuando se toma una acción"""
        pass
```

## 🎮 Tipos de Jugadores Incluidos

### 1. `HumanPlayerStrategy`

- Jugador interactivo controlado por humano
- Solicita entrada por consola para cada decisión

### 2. `SimpleAIStrategy`

- IA básica con comportamiento aleatorio ponderado
- 60% check/call, 20% fold, 15% bet/raise, 5% all-in

### 3. `AggressiveAIStrategy`

- IA más agresiva que prefiere apostar y subir
- 50% bet/raise, 30% check/call, 10% fold, 10% all-in

### 4. `ConservativeAIStrategy`

- IA conservadora que prefiere jugar seguro
- 60% check/call, 30% fold, 8% bet/raise, 2% all-in

## 🚀 Uso Básico

### Crear un Juego Simple

```python
from pokerSimulator import (
    InteractivePokerGame, 
    HumanPlayerStrategy,
    SimpleAIStrategy,
    AggressiveAIStrategy
)

# Crear estrategias para los jugadores
strategies = [
    HumanPlayerStrategy("Mi Nombre"),
    SimpleAIStrategy("Bot Simple"),
    AggressiveAIStrategy("Bot Agresivo")
]

# Configurar el juego
starting_stacks = [10000, 10000, 10000]
blinds = (50, 100)

# Crear y ejecutar
game = InteractivePokerGame(
    player_strategies=strategies,
    starting_stacks=starting_stacks,
    blinds=blinds
)

game.play_hand()
```

### Juego Solo Entre IAs

```python
strategies = [
    SimpleAIStrategy("Bot 1"),
    AggressiveAIStrategy("Bot 2"),
    ConservativeAIStrategy("Bot 3")
]

game = InteractivePokerGame(player_strategies=strategies)
game.play_hand()
```

## 🔧 Crear Estrategias Personalizadas

### Ejemplo: Estrategia que Cuenta Cartas

```python
class CardCountingStrategy(PlayerStrategy):
    def __init__(self, name="Contador"):
        self.name = name
        self.cards_seen = []
    
    def get_name(self):
        return self.name
    
    def make_decision(self, game_state, available_actions, player_index):
        # Analizar cartas comunitarias
        community_cards = []
        try:
            for cards in game_state.board_cards:
                community_cards.extend(cards)
        except (TypeError, AttributeError):
            pass
        
        # Ajustar estrategia basada en cartas vistas
        # ... tu lógica aquí ...
        
        # Retornar decisión
        return "call", amount
    
    def on_action_taken(self, player_index, action_type, amount, description):
        print(f"🧠 {self.name}: {description}")
```

### Ejemplo: Estrategia con Bluff

```python
class BluffingStrategy(PlayerStrategy):
    def __init__(self, name="Bluffer"):
        self.name = name
        self.bluff_frequency = 0.2
    
    def make_decision(self, game_state, available_actions, player_index):
        # Decidir si hacer bluff
        if random.random() < self.bluff_frequency:
            # Buscar acción más agresiva
            for action_type, desc, amount in reversed(available_actions):
                if action_type in ["bet", "raise"]:
                    return action_type, amount
        
        # Comportamiento normal
        # ... lógica estándar ...
```

## 📊 Recolección de Datos

Ejemplo de estrategia que recopila estadísticas:

```python
class DataCollectionStrategy(PlayerStrategy):
    def __init__(self, name="Analizador", base_strategy=None):
        self.name = name
        self.base_strategy = base_strategy or SimpleAIStrategy()
        self.game_data = {
            'hands_played': 0,
            'actions_taken': [],
            'win_rate': 0
        }
    
    def make_decision(self, game_state, available_actions, player_index):
        # Recopilar datos
        self.game_data['hands_played'] += 1
        
        # Usar estrategia base
        decision = self.base_strategy.make_decision(
            game_state, available_actions, player_index
        )
        
        # Registrar decisión
        if decision:
            self.game_data['actions_taken'].append({
                'action': decision[0],
                'amount': decision[1],
                'street': game_state.street_index
            })
        
        return decision
```

## 🎯 Información Disponible en `game_state`

Durante `make_decision()`, tienes acceso a:

- `game_state.street_index`: Calle actual (0=pre-flop, 1=flop, 2=turn, 3=river)
- `game_state.board_cards`: Cartas comunitarias
- `game_state.hole_cards[player_index]`: Tus cartas (solo las tuyas)
- `game_state.stacks`: Fichas de cada jugador
- `game_state.bets`: Apuestas actuales de cada jugador
- `game_state.player_count`: Número total de jugadores
- `game_state.actor_indices`: Índices de jugadores que pueden actuar

## 🎮 Acciones Disponibles

El parámetro `available_actions` contiene tuplas de:

- `(action_type, description, amount)`

Tipos de acción:

- `"fold"`: Retirarse
- `"check"`: Pasar (cuando no hay apuesta)
- `"call"`: Igualar apuesta
- `"bet"`: Apostar (cuando no hay apuesta previa)
- `"raise"`: Subir apuesta existente
- `"allin"`: Apostar todas las fichas

## 📁 Archivos del Proyecto

- `pokerSimulator.py`: Código principal del simulador
- `example_custom_players.py`: Ejemplos de jugadores personalizados
- `README.md`: Esta documentación

## 🚀 Ejecutar Ejemplos

```bash
# Ejecutar simulador básico
python pokerSimulator.py

# Ejecutar ejemplos personalizados
python example_custom_players.py
```

## 🔄 Compatibilidad con Código Anterior

El código mantiene compatibilidad con versiones anteriores. Los métodos legacy como `get_human_action()` y `get_ai_action()` siguen funcionando pero ahora redirigen a la nueva arquitectura.

## 🎲 Ideas para Estrategias Personalizadas

1. **Análisis de Patrones**: Analizar comportamiento de oponentes
2. **Gestión de Bankroll**: Ajustar apuestas según fichas restantes
3. **Análisis de Posición**: Comportamiento diferente según posición en la mesa
4. **Machine Learning**: Usar modelos entrenados para decisiones
5. **Simulación Monte Carlo**: Calcular probabilidades de ganar
6. **Análisis de Rangos**: Estimar rangos de cartas de oponentes

¡Experimenta y crea tus propias estrategias avanzadas!
