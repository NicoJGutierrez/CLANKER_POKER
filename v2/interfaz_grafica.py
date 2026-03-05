from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from bots_ejemplo import ConservadorBot, SiempreJuegaBot
from engine import PokerEngine
from mi_bot import MiBot


class AppPoker(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Poker Bots - Visualizador de Jugadas")
        self.geometry("780x520")

        self.bots = [
            MiBot("MiBot"),
            SiempreJuegaBot("SiempreJuega"),
            ConservadorBot("Conservador"),
        ]
        self.engine = PokerEngine(bots=self.bots, fichas_iniciales=100)

        self.dealer = 0
        self.eventos_pendientes: list[str] = []
        self.animando = False

        self._crear_ui()
        self._actualizar_tabla_fichas()

    def _crear_ui(self) -> None:
        contenedor = ttk.Frame(self, padding=12)
        contenedor.pack(fill="both", expand=True)

        barra = ttk.Frame(contenedor)
        barra.pack(fill="x", pady=(0, 8))

        self.btn_jugar = ttk.Button(
            barra, text="Jugar ronda", command=self.jugar_ronda)
        self.btn_jugar.pack(side="left")

        self.lbl_estado = ttk.Label(barra, text="Listo")
        self.lbl_estado.pack(side="left", padx=12)

        marco = ttk.Frame(contenedor)
        marco.pack(fill="both", expand=True)

        izquierda = ttk.LabelFrame(marco, text="Fichas")
        izquierda.pack(side="left", fill="y", padx=(0, 8))

        self.tabla_fichas = tk.Listbox(izquierda, width=26, height=20)
        self.tabla_fichas.pack(fill="both", expand=True, padx=8, pady=8)

        derecha = ttk.LabelFrame(marco, text="Jugadas")
        derecha.pack(side="left", fill="both", expand=True)

        self.texto_log = tk.Text(derecha, wrap="word", state="disabled")
        self.texto_log.pack(fill="both", expand=True, padx=8, pady=8)

    def jugar_ronda(self) -> None:
        if self.animando:
            return

        self._limpiar_log()
        self.lbl_estado.config(text="Jugando...")
        self.btn_jugar.config(state="disabled")

        resultado = self.engine.jugar_ronda(
            dealer=self.dealer, mostrar_logs=False)
        self.dealer = (self.dealer + 1) % len(self.bots)

        self.eventos_pendientes = resultado.eventos[:]
        self.eventos_pendientes.append("")
        self.eventos_pendientes.append("Resumen:")
        self.eventos_pendientes.append(f"Pozo final: {resultado.pozo_final}")
        self.eventos_pendientes.append(f"Mesa final: {resultado.mesa}")

        for i, bot in enumerate(self.bots):
            self.eventos_pendientes.append(
                f"{bot.nombre} -> fichas: {resultado.fichas_finales[i]}")

        self.animando = True
        self._mostrar_siguiente_evento()

    def _mostrar_siguiente_evento(self) -> None:
        if not self.eventos_pendientes:
            self.animando = False
            self.btn_jugar.config(state="normal")
            self.lbl_estado.config(text="Ronda finalizada")
            self._actualizar_tabla_fichas()
            return

        evento = self.eventos_pendientes.pop(0)
        self._agregar_log(evento)
        self.after(700, self._mostrar_siguiente_evento)

    def _actualizar_tabla_fichas(self) -> None:
        self.tabla_fichas.delete(0, tk.END)
        for i, bot in enumerate(self.bots):
            self.tabla_fichas.insert(
                tk.END, f"{bot.nombre}: {self.engine.fichas[i]} fichas")

    def _agregar_log(self, linea: str) -> None:
        self.texto_log.config(state="normal")
        self.texto_log.insert(tk.END, linea + "\n")
        self.texto_log.see(tk.END)
        self.texto_log.config(state="disabled")

    def _limpiar_log(self) -> None:
        self.texto_log.config(state="normal")
        self.texto_log.delete("1.0", tk.END)
        self.texto_log.config(state="disabled")


if __name__ == "__main__":
    app = AppPoker()
    app.mainloop()
