# Requisitos del Simulador de Poker

## Dependencias Necesarias

Para ejecutar este simulador necesitas instalar la librería `pokerkit`:

```bash
pip install pokerkit
```

## Verificación de Instalación

```python
# Ejecuta este código para verificar que todo está instalado correctamente
try:
    from pokerkit import Automation, Mode, NoLimitTexasHoldem
    print("✅ pokerkit instalado correctamente")
    
    from pokerSimulator import PlayerStrategy, InteractivePokerGame
    print("✅ Simulador importado correctamente")
    
    print("🎯 ¡Todo listo para jugar!")
    
except ImportError as e:
    print(f"❌ Error de importación: {e}")
    print("Instala las dependencias con: pip install pokerkit")
```

## Estructura de Archivos

```python
CLANKER_POKER/
├── pokerSimulator.py          # Simulador principal con jugadores personalizables
├── example_custom_players.py  # Ejemplos de jugadores personalizados
├── requirements.md           # Este archivo
└── README.md                  # Documentación completa
```

## Ejecutar el Simulador

Una vez instaladas las dependencias:

```bash
# Juego básico
python pokerSimulator.py

# Ejemplos con jugadores personalizados
python example_custom_players.py
```
