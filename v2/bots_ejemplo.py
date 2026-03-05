from __future__ import annotations

from typing import Any

from poker_bot import PokerBot


class SiempreJuegaBot(PokerBot):
    """Bot de prueba: nunca se retira."""

    def actuar(self, estado: dict[str, Any], memoria: dict[str, Any]) -> str:
        memoria["turnos_jugados"] = memoria.get("turnos_jugados", 0) + 1

        por_igualar = estado["apuesta_actual"] - estado["aportado_en_ronda"]
        if por_igualar > 0:
            return "call"
        return "check"


class ConservadorBot(PokerBot):
    """
    Bot simple:
    - Preflop: juega manos medias/fuertes, foldea muy débiles si hay que pagar.
    - Si puede pasar gratis, pasa.
    """

    def actuar(self, estado: dict[str, Any], memoria: dict[str, Any]) -> str:
        mano = estado["mano"]
        por_igualar = estado["apuesta_actual"] - estado["aportado_en_ronda"]

        # Persistencia de memoria para análisis del alumno.
        memoria["decisiones"] = memoria.get("decisiones", 0) + 1

        fuerza = self._fuerza_preflop(mano)
        umbral = memoria.get("umbral_preflop", 0.45)

        if por_igualar <= 0:
            return "check"

        if fuerza >= umbral:
            return "call"
        return "fold"

    def _fuerza_preflop(self, mano: list[str]) -> float:
        valor_rango = {
            "2": 2,
            "3": 3,
            "4": 4,
            "5": 5,
            "6": 6,
            "7": 7,
            "8": 8,
            "9": 9,
            "T": 10,
            "J": 11,
            "Q": 12,
            "K": 13,
            "A": 14,
        }

        rank1 = valor_rango[mano[0][0]]
        rank2 = valor_rango[mano[1][0]]
        suited = mano[0][1] == mano[1][1]
        pareja = rank1 == rank2

        if pareja:
            return 0.65 + (rank1 / 20)

        alto = max(rank1, rank2)
        bajo = min(rank1, rank2)

        fuerza = (alto + bajo) / 30
        if suited:
            fuerza += 0.08
        if abs(rank1 - rank2) <= 2:
            fuerza += 0.05

        return min(fuerza, 0.95)
