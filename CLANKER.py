from deuces import Evaluator


def elegir_jugada(mano, cartas_en_mesa, otros_jugadores, pozo: int, num_fichas: int, situación: bool):
    """
    Elige una jugada basada en la mano del jugador, los otros jugadores y el pozo.

    :param mano: Mano de cartas de clanker.
    :param otros_jugadores: Cantidad de otros jugadores participando de la mesa y su número de fichas restantes.
    :param pozo: Cantidad de fichas en el pozo.
    :param num_fichas: Número total de fichas actual de clanker.
    :return: Tupla con la jugada elegida (tipo, num_fichas).
    :param situación: Indica si alguien ha apostado antes o no.
    """
    # Implementación de la lógica para elegir la jugada
    EV = valor_esperado(mano, cartas_en_mesa, len(otros_jugadores), pozo)

    # Aquí se puede agregar la lógica específica del juego Clanker
    if situación:
        if EV > 1.8:
            return "Apostar", num_fichas
        elif EV > 1.4:
            return "Apostar", min(num_fichas, pozo)
        elif EV > 1.1:
            return "Igualar", 0
        else:
            return "Retirarse", 0
    else:
        if EV > 1.8:
            return "Apostar", num_fichas
        elif EV > 1.4:
            return "Apostar", min(num_fichas, pozo)
        else:
            return "Pasar", 0


def valor_esperado(mano, cartas_en_mesa, num_otros_jugadores: int, pozo: int):
    return equity(mano, cartas_en_mesa, num_otros_jugadores) * (num_otros_jugadores + 1)


def equity(mano, cartas_en_mesa):
    evaluator = Evaluator()
    return 1 - ((1 - evaluator.evaluate(mano, cartas_en_mesa))/7462)
