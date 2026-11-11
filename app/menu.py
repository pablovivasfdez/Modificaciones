"""Menú interactivo de la aplicación de terminal."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Final, TextIO

EXIT_OPTION: Final[int] = 5


@dataclass(frozen=True)
class MenuOption:
    """Una opción numerada del menú."""

    key: int
    label: str


MENU_OPTIONS: Final[tuple[MenuOption, ...]] = (
    MenuOption(1, "Regenerar laberinto"),
    MenuOption(2, "Mostrar/ocultar camino más corto"),
    MenuOption(3, "Cambiar color de paredes (ciclo de temas)"),
    MenuOption(4, "Cambiar algoritmo y regenerar"),
    MenuOption(5, "Salir"),
)


def render_menu(
    theme_name: str,
    algorithm: str,
    show_path: bool,
) -> str:
    """Construye el texto del menú con el estado actual."""
    path_state = "visible" if show_path else "oculto"
    lines = [
        "",
        "=== A-Maze-ing ===",
        f"Tema: {theme_name} | Algoritmo: {algorithm} | "
        f"Camino: {path_state}",
        "",
    ]
    for option in MENU_OPTIONS:
        lines.append(f"{option.key}. {option.label}")
    return "\n".join(lines)


class Menu:
    """Lector de opciones del menú con validación de entrada.

    Args:
        input_stream: Flujo de entrada. Por defecto, ``sys.stdin``.
        output_stream: Flujo de salida. Por defecto, ``sys.stdout``.
    """

    def __init__(
        self,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
    ) -> None:
        self.input_stream = (
            sys.stdin if input_stream is None else input_stream
        )
        self.output_stream = (
            sys.stdout if output_stream is None else output_stream
        )

    def prompt(
        self,
        theme_name: str,
        algorithm: str,
        show_path: bool,
    ) -> int | None:
        """Pide una opción válida.

        Returns:
            El número de opción elegido, o ``None`` si la entrada se
            ha cerrado inesperadamente.
        """
        while True:
            self.output_stream.write(
                render_menu(theme_name, algorithm, show_path) + "\n"
            )
            self.output_stream.write("> ")
            self.output_stream.flush()
            raw_line = self.input_stream.readline()
            if raw_line == "":
                self.output_stream.write("\n")
                return None
            text = raw_line.strip()
            try:
                choice = int(text)
            except ValueError:
                self._show_invalid()
                continue
            if choice < 1 or choice > EXIT_OPTION:
                self._show_invalid()
                continue
            return choice

    def _show_invalid(self) -> None:
        """Informa de una opción no válida sin terminar el programa."""
        self.output_stream.write(
            "Opción no válida. Introduce un número del 1 al "
            f"{EXIT_OPTION}.\n"
        )
