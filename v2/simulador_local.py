from __future__ import annotations

from bots_ejemplo import ConservadorBot, SiempreJuegaBot
from engine import PokerEngine
from mi_bot import MiBot


def main() -> None:
    bots = [
        MiBot("MiBot"),
        SiempreJuegaBot("SiempreJuega"),
        ConservadorBot("Conservador"),
    ]

    engine = PokerEngine(bots=bots, fichas_iniciales=100)

    print("=== Simulación local (1 ronda) ===")
    resultado = engine.jugar_ronda(dealer=0, mostrar_logs=False)
    for evento in resultado.eventos:
        print(evento)

    print("\nResumen:")
    print("Pozo:", resultado.pozo_final)
    print("Mesa:", resultado.mesa)
    print("Fichas finales:")
    for i, bot in enumerate(bots):
        print(f"- {bot.nombre}: {resultado.fichas_finales[i]}")

    print("\nMemoria de MiBot:", engine.memorias[0])


if __name__ == "__main__":
    main()
