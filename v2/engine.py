from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from treys import Card, Deck, Evaluator

from poker_bot import PokerBot


@dataclass
class ResultadoRonda:
    pozo_final: int
    ganadores: list[int]
    fichas_finales: list[int]
    mesa: list[str]
    eventos: list[str]


class PokerEngine:
    """
    Motor didáctico de una ronda de Texas Hold'em (sin subidas, solo fold/call/check).

    Diseñado para estudiantes: estado simple en diccionario y memorias persistentes.
    """

    def __init__(
        self,
        bots: list[PokerBot],
        fichas_iniciales: int = 100,
        small_blind: int = 1,
        big_blind: int = 2,
    ):
        if len(bots) < 2:
            raise ValueError("Se requieren al menos 2 bots.")

        self.bots = bots
        self.n = len(bots)
        self.fichas = [fichas_iniciales for _ in bots]
        self.small_blind = small_blind
        self.big_blind = big_blind

        # Memoria persistente por bot durante toda la partida.
        self.memorias: list[dict[str, Any]] = [{} for _ in bots]

    def jugar_ronda(self, dealer: int = 0, mostrar_logs: bool = True) -> ResultadoRonda:
        activos = [self.fichas[i] > 0 for i in range(self.n)]
        if sum(activos) < 2:
            raise RuntimeError("No hay suficientes jugadores con fichas para iniciar ronda.")

        mazo = Deck()
        evaluador = Evaluator()

        manos = [mazo.draw(2) for _ in range(self.n)]
        manos_str = [[Card.int_to_str(c) for c in mano] for mano in manos]
        retirado = [not activos[i] for i in range(self.n)]
        mesa: list[int] = []

        sb = (dealer + 1) % self.n
        bb = (dealer + 2) % self.n
        eventos: list[str] = [
            f"Dealer: {self.bots[dealer].nombre}",
            f"Small blind: {self.bots[sb].nombre} ({self.small_blind})",
            f"Big blind: {self.bots[bb].nombre} ({self.big_blind})",
            "Manos iniciales:",
        ]
        for i, bot in enumerate(self.bots):
            eventos.append(f"- {bot.nombre}: {manos_str[i]}")

        pozo = 0
        preflop_aportado = [0 for _ in range(self.n)]
        pozo += self._post_blind(sb, self.small_blind, preflop_aportado)
        pozo += self._post_blind(bb, self.big_blind, preflop_aportado)

        # Preflop: empieza a la izquierda de BB.
        inicio_preflop = (bb + 1) % self.n
        orden_preflop = [(inicio_preflop + k) % self.n for k in range(self.n)]
        pozo = self._jugar_calle(
            nombre_calle="Preflop",
            orden=orden_preflop,
            manos=manos,
            mesa=mesa,
            retirado=retirado,
            dealer=dealer,
            sb=sb,
            bb=bb,
            pozo=pozo,
            eventos=eventos,
            mostrar_logs=mostrar_logs,
            aportado_inicial=preflop_aportado,
        )

        vivos = [i for i in range(self.n) if not retirado[i]]
        if len(vivos) == 1:
            ganador = vivos[0]
            self.fichas[ganador] += pozo
            eventos.append("--- Showdown ---")
            eventos.append("No hubo showdown (todos se retiraron antes).")
            eventos.append(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            if mostrar_logs:
                print("--- Showdown ---")
                print("No hubo showdown (todos se retiraron antes).")
                print(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            return ResultadoRonda(pozo, [ganador], self.fichas[:], [], eventos)

        # Flop
        mesa.extend(mazo.draw(3))
        mesa_str = [Card.int_to_str(c) for c in mesa]
        eventos.append(f"Flop: {mesa_str}")
        if mostrar_logs:
            print(f"Flop: {mesa_str}")

        # Postflop: empieza small blind (izquierda del dealer).
        inicio_postflop = (dealer + 1) % self.n
        orden_postflop = [(inicio_postflop + k) % self.n for k in range(self.n)]
        pozo = self._jugar_calle(
            nombre_calle="Flop",
            orden=orden_postflop,
            manos=manos,
            mesa=mesa,
            retirado=retirado,
            dealer=dealer,
            sb=sb,
            bb=bb,
            pozo=pozo,
            eventos=eventos,
            mostrar_logs=mostrar_logs,
        )

        vivos = [i for i in range(self.n) if not retirado[i]]
        if len(vivos) == 1:
            ganador = vivos[0]
            self.fichas[ganador] += pozo
            eventos.append("--- Showdown ---")
            eventos.append("No hubo showdown (todos se retiraron antes).")
            eventos.append(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            if mostrar_logs:
                print("--- Showdown ---")
                print("No hubo showdown (todos se retiraron antes).")
                print(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            return ResultadoRonda(pozo, [ganador], self.fichas[:], [Card.int_to_str(c) for c in mesa], eventos)

        # Turn
        mesa.extend(mazo.draw(1))
        mesa_str = [Card.int_to_str(c) for c in mesa]
        eventos.append(f"Turn: {mesa_str}")
        if mostrar_logs:
            print(f"Turn: {mesa_str}")

        pozo = self._jugar_calle(
            nombre_calle="Turn",
            orden=orden_postflop,
            manos=manos,
            mesa=mesa,
            retirado=retirado,
            dealer=dealer,
            sb=sb,
            bb=bb,
            pozo=pozo,
            eventos=eventos,
            mostrar_logs=mostrar_logs,
        )

        vivos = [i for i in range(self.n) if not retirado[i]]
        if len(vivos) == 1:
            ganador = vivos[0]
            self.fichas[ganador] += pozo
            eventos.append("--- Showdown ---")
            eventos.append("No hubo showdown (todos se retiraron antes).")
            eventos.append(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            if mostrar_logs:
                print("--- Showdown ---")
                print("No hubo showdown (todos se retiraron antes).")
                print(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            return ResultadoRonda(pozo, [ganador], self.fichas[:], [Card.int_to_str(c) for c in mesa], eventos)

        # River
        mesa.extend(mazo.draw(1))
        mesa_str = [Card.int_to_str(c) for c in mesa]
        eventos.append(f"River: {mesa_str}")
        if mostrar_logs:
            print(f"River: {mesa_str}")

        pozo = self._jugar_calle(
            nombre_calle="River",
            orden=orden_postflop,
            manos=manos,
            mesa=mesa,
            retirado=retirado,
            dealer=dealer,
            sb=sb,
            bb=bb,
            pozo=pozo,
            eventos=eventos,
            mostrar_logs=mostrar_logs,
        )

        vivos = [i for i in range(self.n) if not retirado[i]]
        if len(vivos) == 1:
            ganador = vivos[0]
            self.fichas[ganador] += pozo
            eventos.append("--- Showdown ---")
            eventos.append("No hubo showdown (todos se retiraron antes).")
            eventos.append(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            if mostrar_logs:
                print("--- Showdown ---")
                print("No hubo showdown (todos se retiraron antes).")
                print(f"Ganador sin showdown: {self.bots[ganador].nombre} (+{pozo})")
            return ResultadoRonda(pozo, [ganador], self.fichas[:], [Card.int_to_str(c) for c in mesa], eventos)

        eventos.append("--- Showdown ---")
        for i in vivos:
            eventos.append(f"{self.bots[i].nombre} muestra {manos_str[i]}")

        ganadores = self._resolver_showdown(vivos, manos, mesa, evaluador)
        self._repartir_pozo(pozo, ganadores)
        mesa_str = [Card.int_to_str(c) for c in mesa]
        eventos.append(f"Mesa final: {mesa_str}")
        nombres = ", ".join(self.bots[i].nombre for i in ganadores)
        eventos.append(f"Ganador(es): {nombres} | Pozo: {pozo}")

        if mostrar_logs:
            print("--- Showdown ---")
            for i in vivos:
                print(f"{self.bots[i].nombre} muestra {manos_str[i]}")
            print(f"Mesa: {mesa_str}")
            print(f"Ganador(es): {nombres} | Pozo: {pozo}")

        return ResultadoRonda(pozo, ganadores, self.fichas[:], mesa_str, eventos)

    def _jugar_calle(
        self,
        nombre_calle: str,
        orden: list[int],
        manos: list[list[int]],
        mesa: list[int],
        retirado: list[bool],
        dealer: int,
        sb: int,
        bb: int,
        pozo: int,
        eventos: list[str],
        mostrar_logs: bool,
        aportado_inicial: list[int] | None = None,
    ) -> int:
        if aportado_inicial is None:
            aportado = [0 for _ in range(self.n)]
        else:
            aportado = aportado_inicial[:]

        apuesta_actual = max(aportado)
        quienes_actuaron: set[int] = set()
        idx = 0
        eventos.append(f"--- {nombre_calle} ---")

        while True:
            vivos = [i for i in range(self.n) if not retirado[i]]
            if len(vivos) <= 1:
                break

            if apuesta_actual == 0:
                pueden_actuar = [i for i in vivos if self.fichas[i] > 0]
                if all(i in quienes_actuaron for i in pueden_actuar):
                    break
            else:
                if all(aportado[i] == apuesta_actual for i in vivos):
                    break

            jugador = orden[idx]
            idx = (idx + 1) % len(orden)

            if retirado[jugador] or self.fichas[jugador] <= 0:
                continue

            por_igualar = max(0, apuesta_actual - aportado[jugador])
            estado = {
                "mano": [Card.int_to_str(c) for c in manos[jugador]],
                "mesa": [Card.int_to_str(c) for c in mesa],
                "pot": pozo,
                "fichas_propias": self.fichas[jugador],
                "posición": jugador,
                "dealer": dealer,
                "small_blind": sb,
                "big_blind": bb,
                "calle": nombre_calle.lower(),
                "apuesta_actual": apuesta_actual,
                "aportado_en_ronda": aportado[jugador],
                "jugadores_activos": [j for j in range(self.n) if not retirado[j]],
            }

            accion = self._accion_segura(jugador, estado)

            if accion == "fold":
                retirado[jugador] = True
                eventos.append(f"{self.bots[jugador].nombre}: fold")
                if mostrar_logs:
                    print(f"{self.bots[jugador].nombre}: fold")
                continue

            if por_igualar > 0:
                if self.fichas[jugador] < por_igualar:
                    retirado[jugador] = True
                    eventos.append(f"{self.bots[jugador].nombre}: fold (sin fichas para igualar)")
                    if mostrar_logs:
                        print(f"{self.bots[jugador].nombre}: fold (sin fichas para igualar)")
                    continue

                pago = por_igualar
                self.fichas[jugador] -= pago
                aportado[jugador] += pago
                pozo += pago
                eventos.append(f"{self.bots[jugador].nombre}: call ({pago})")
                if mostrar_logs:
                    print(f"{self.bots[jugador].nombre}: call ({pago})")
                quienes_actuaron.add(jugador)
                continue

            # por_igualar == 0
            if accion == "bet":
                apuesta = min(self.big_blind, self.fichas[jugador])
                if apuesta <= 0:
                    eventos.append(f"{self.bots[jugador].nombre}: check")
                    if mostrar_logs:
                        print(f"{self.bots[jugador].nombre}: check")
                else:
                    self.fichas[jugador] -= apuesta
                    aportado[jugador] += apuesta
                    pozo += apuesta
                    apuesta_actual = aportado[jugador]
                    eventos.append(f"{self.bots[jugador].nombre}: bet ({apuesta})")
                    if mostrar_logs:
                        print(f"{self.bots[jugador].nombre}: bet ({apuesta})")
            else:
                eventos.append(f"{self.bots[jugador].nombre}: check")
                if mostrar_logs:
                    print(f"{self.bots[jugador].nombre}: check")

            quienes_actuaron.add(jugador)

        return pozo

    def _post_blind(self, jugador: int, cantidad: int, aportado: list[int]) -> int:
        pago = min(cantidad, self.fichas[jugador])
        self.fichas[jugador] -= pago
        aportado[jugador] += pago
        return pago

    def _accion_segura(self, i: int, estado: dict[str, Any]) -> str:
        try:
            accion = self.bots[i].actuar(estado, self.memorias[i])
        except Exception:
            return "fold"

        if not isinstance(accion, str):
            return "fold"

        accion = accion.lower().strip()
        if accion not in {"fold", "call", "check", "bet"}:
            return "fold"
        return accion

    def _resolver_showdown(
        self,
        vivos: list[int],
        manos: list[list[int]],
        mesa: list[int],
        evaluador: Evaluator,
    ) -> list[int]:
        mejores: list[int] = []
        valor_mejor: int | None = None

        for i in vivos:
            valor = evaluador.evaluate(mesa, manos[i])
            if valor_mejor is None or valor < valor_mejor:
                valor_mejor = valor
                mejores = [i]
            elif valor == valor_mejor:
                mejores.append(i)

        return mejores

    def _repartir_pozo(self, pozo: int, ganadores: list[int]) -> None:
        if not ganadores:
            return

        base = pozo // len(ganadores)
        resto = pozo % len(ganadores)

        for i, jugador in enumerate(ganadores):
            premio = base + (1 if i < resto else 0)
            self.fichas[jugador] += premio


if __name__ == "__main__":
    from bots_ejemplo import ConservadorBot, SiempreJuegaBot

    bots = [
        SiempreJuegaBot("Bot_A"),
        ConservadorBot("Bot_B"),
        SiempreJuegaBot("Bot_C"),
    ]

    engine = PokerEngine(bots=bots, fichas_iniciales=50)
    resultado = engine.jugar_ronda(dealer=0, mostrar_logs=True)
    print("Fichas finales:", resultado.fichas_finales)
