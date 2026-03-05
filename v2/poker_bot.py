from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class PokerBot(ABC):
    """
    Clase base para bots de Texas Hold'em.

    Cada bot debe implementar `actuar(estado, memoria)` y devolver una acción:
    - "fold"  -> retirarse
    - "call"  -> igualar apuesta actual
    - "check" -> pasar (si no hay apuesta por igualar)
    - "bet"   -> apostar (solo cuando no hay apuesta actual en la calle)

    `memoria` es un diccionario persistente durante toda la partida.
    """

    def __init__(self, nombre: str):
        self.nombre = nombre

    @abstractmethod
    def actuar(self, estado: dict[str, Any], memoria: dict[str, Any]) -> str:
        raise NotImplementedError
