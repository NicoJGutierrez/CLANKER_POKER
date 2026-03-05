from __future__ import annotations

from typing import Any

from poker_bot import PokerBot


class MiBot(PokerBot):
    """
    Plantilla para estudiantes.

    Edita la lógica de `actuar` usando `estado` y guardando datos en `memoria`.
    """

    def actuar(self, estado: dict[str, Any], memoria: dict[str, Any]) -> str:
        # Ejemplo de memoria persistente:
        memoria["turnos"] = memoria.get("turnos", 0) + 1

        por_igualar = estado["apuesta_actual"] - estado["aportado_en_ronda"]

        if por_igualar > 0:
            return "call"
        return "check"
