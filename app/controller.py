"""Orquestación entre configuración, generación, salida y menú."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from mazegen import Maze, MazeError, MazeGenerator

from .config import ALGORITHMS, MazeConfig
from .menu import EXIT_OPTION, Menu
from .output import write_maze
from .renderers.base import Renderer
from .renderers.console import ConsoleRenderer
from .themes import next_theme


@dataclass(frozen=True)
class GeneratedMaze:
    """Resultado completo de una generación.

    Attributes:
        maze: Laberinto generado.
        solution: Camino más corto en formato ``N/E/S/W``.
        seed: Semilla efectiva usada por el generador.
        warning: Aviso opcional del generador.
    """

    maze: Maze
    solution: str
    seed: int
    warning: str | None


def load_configuration(path: str | Path) -> MazeConfig:
    """Carga la configuración desde ``path``."""
    return MazeConfig.from_file(path)


def generate_maze(
    config: MazeConfig,
    algorithm: str | None = None,
    seed: int | None = None,
) -> GeneratedMaze:
    """Genera un laberinto y resuelve su camino más corto.

    Args:
        config: Configuración validada.
        algorithm: Algoritmo a usar. Por defecto, el de la config.
        seed: Semilla a usar. Si es ``None`` se usa la de la config;
            si la config tampoco tiene, el generador elige una.
    """
    chosen_algorithm = config.algorithm if algorithm is None else algorithm
    chosen_seed = config.seed if seed is None else seed
    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit=config.exit,
        perfect=config.perfect,
        seed=chosen_seed,
        algorithm=chosen_algorithm,
    )
    maze = generator.generate()
    return GeneratedMaze(
        maze=maze,
        solution=generator.solve(),
        seed=generator.seed,
        warning=generator.last_warning,
    )


def menu_available(input_stream: TextIO) -> bool:
    """Indica si debe mostrarse el menú interactivo."""
    flag = os.environ.get("AMAZEING_NO_MENU", "").strip().lower()
    if flag in {"1", "true", "yes", "on"}:
        return False
    try:
        return bool(input_stream.isatty())
    except (AttributeError, OSError, ValueError):
        return False


class MazeController:
    """Coordina el ciclo de vida completo de la aplicación."""

    def __init__(
        self,
        config: MazeConfig,
        renderer: Renderer | None = None,
        input_stream: TextIO | None = None,
        output_stream: TextIO | None = None,
        error_stream: TextIO | None = None,
    ) -> None:
        self.config = config
        self.renderer = (
            ConsoleRenderer() if renderer is None else renderer
        )
        self.input_stream = (
            sys.stdin if input_stream is None else input_stream
        )
        self.output_stream = (
            sys.stdout if output_stream is None else output_stream
        )
        self.error_stream = (
            sys.stderr if error_stream is None else error_stream
        )
        self.algorithm = config.algorithm
        self.theme = config.theme
        self.show_path = False
        self.regenerations = 0
        self.generated: GeneratedMaze | None = None
        self.menu = Menu(self.input_stream, self.output_stream)

    def generate(self) -> GeneratedMaze:
        """Genera el laberinto actual según el estado del controlador."""
        generated = generate_maze(
            self.config,
            self.algorithm,
            self._next_seed(),
        )
        self.generated = generated
        return generated

    def write_output(self) -> Path:
        """Escribe el laberinto actual en el fichero configurado."""
        generated = self._require_generated()
        return write_maze(
            generated.maze,
            generated.solution,
            self.config.output_file,
        )

    def render(self) -> str:
        """Devuelve el laberinto actual renderizado."""
        generated = self._require_generated()
        return self.renderer.render(
            generated.maze,
            self.show_path,
            self.theme,
        )

    def regenerate(self) -> GeneratedMaze:
        """Regenera el laberinto y actualiza el fichero de salida."""
        self.regenerations += 1
        generated = self.generate()
        self.write_output()
        return generated

    def toggle_path(self) -> bool:
        """Cambia la visibilidad del camino más corto."""
        self.show_path = not self.show_path
        return self.show_path

    def cycle_theme(self) -> str:
        """Avanza al siguiente tema de colores."""
        self.theme = next_theme(self.theme)
        return self.theme

    def change_algorithm(self) -> str:
        """Alterna el algoritmo y regenera el laberinto."""
        current = self.algorithm
        if current in ALGORITHMS:
            index = ALGORITHMS.index(current)
        else:
            index = -1
        self.algorithm = ALGORITHMS[(index + 1) % len(ALGORITHMS)]
        self.regenerate()
        return self.algorithm

    def run(self, interactive: bool | None = None) -> None:
        """Genera, guarda y muestra el laberinto, y abre el menú.

        Args:
            interactive: Fuerza o desactiva el menú. Si es ``None``
                se decide a partir de ``stdin`` y de
                ``AMAZEING_NO_MENU``.
        """
        self.generate()
        self.write_output()
        self._announce_warning()
        self._print_maze()

        if interactive is None:
            interactive = menu_available(self.input_stream)
        if not interactive:
            return
        self.run_menu()

    def run_menu(self) -> None:
        """Ejecuta el bucle del menú hasta que el usuario sale."""
        while True:
            choice = self.menu.prompt(
                self.theme,
                self.algorithm,
                self.show_path,
            )
            if choice is None or choice == EXIT_OPTION:
                return
            self._run_choice(choice)
            self._print_maze()

    def _run_choice(self, choice: int) -> None:
        """Ejecuta la acción asociada a una opción del menú."""
        if choice == 1:
            self.regenerate()
            self._announce_warning()
        elif choice == 2:
            self.toggle_path()
        elif choice == 3:
            self.cycle_theme()
        elif choice == 4:
            self.change_algorithm()
            self._announce_warning()

    def _next_seed(self) -> int | None:
        """Calcula la semilla de la siguiente generación."""
        if self.config.seed is None:
            return None
        return self.config.seed + self.regenerations

    def _require_generated(self) -> GeneratedMaze:
        """Devuelve la generación actual o lanza un error claro."""
        if self.generated is None:
            raise MazeError(
                "Todavía no se ha generado ningún laberinto."
            )
        return self.generated

    def _print_maze(self) -> None:
        """Escribe el laberinto actual en la salida."""
        self.output_stream.write(self.render() + "\n")
        self.output_stream.flush()

    def _announce_warning(self) -> None:
        """Muestra los avisos no bloqueantes del generador."""
        generated = self.generated
        if generated is None or generated.warning is None:
            return
        self.error_stream.write(f"Aviso: {generated.warning}\n")
        self.error_stream.flush()
