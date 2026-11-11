"""Renderizador ASCII/ANSI portable para terminales."""

from __future__ import annotations

import os
import sys
from typing import Final

from mazegen import Direction, Maze, MazeError
from mazegen.solver import shortest_path

from ..themes import Theme, get_theme, paint

CELL_WIDTH: Final[int] = 3
PathCells = set[tuple[int, int]]

_STEP: Final[dict[str, tuple[int, int]]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}


def _colors_enabled() -> bool:
    """Indica si se pueden usar colores ANSI en la salida actual."""
    if "NO_COLOR" in os.environ:
        return False
    try:
        return bool(sys.stdout.isatty())
    except (AttributeError, OSError, ValueError):
        return False


def _path_cells(maze: Maze, path: str) -> PathCells:
    """Convierte una secuencia ``N/E/S/W`` en celdas visitadas."""
    x, y = maze.entry
    cells: PathCells = {(x, y)}
    for raw_step in path:
        step = raw_step.upper()
        delta = _STEP.get(step)
        if delta is None:
            raise MazeError(
                f"El camino contiene un movimiento no válido: "
                f"'{raw_step}'."
            )
        next_x = x + delta[0]
        next_y = y + delta[1]
        if not maze.is_inside(next_x, next_y):
            raise MazeError(
                "El camino sale del laberinto en la celda "
                f"({next_x},{next_y})."
            )
        x, y = next_x, next_y
        cells.add((x, y))
    return cells


class ConsoleRenderer:
    """Dibuja un laberinto con paredes, símbolos y colores ANSI.

    Args:
        use_color: Fuerza o desactiva el color. Si es ``None`` se
            detecta automáticamente a partir de ``NO_COLOR`` y de si
            la salida estándar es un TTY.
    """

    def __init__(self, use_color: bool | None = None) -> None:
        self.use_color = (
            _colors_enabled() if use_color is None else use_color
        )

    def render(
        self,
        maze: Maze,
        show_path: bool = False,
        theme_name: str = "midnight",
        path: str | None = None,
    ) -> str:
        """Devuelve el laberinto listo para imprimir.

        Args:
            maze: Laberinto que se quiere dibujar.
            show_path: Si debe superponerse el camino más corto.
            theme_name: Nombre del tema de colores.
            path: Camino opcional en formato ``N/E/S/W``. Si se omite
                y ``show_path`` es verdadero, se calcula con el solver.
        """
        theme = get_theme(theme_name)
        path_cells: PathCells = set()
        if show_path:
            if path is None:
                path = shortest_path(maze)
            path_cells = _path_cells(maze, path)

        lines: list[str] = [
            self._horizontal_line(maze, 0, Direction.NORTH, theme)
        ]
        for y in range(maze.height):
            lines.append(self._cells_line(maze, y, theme, path_cells))
            lines.append(
                self._horizontal_line(maze, y, Direction.SOUTH, theme)
            )
        return "\n".join(lines)

    def _horizontal_line(
        self,
        maze: Maze,
        y: int,
        direction: Direction,
        theme: Theme,
    ) -> str:
        """Dibuja una línea horizontal de muros."""
        parts: list[str] = [self._paint("+", theme.wall)]
        for x in range(maze.width):
            closed = maze.has_wall(x, y, direction)
            segment = "---" if closed else " " * CELL_WIDTH
            parts.append(self._paint(segment, theme.wall))
            parts.append(self._paint("+", theme.wall))
        return "".join(parts)

    def _cells_line(
        self,
        maze: Maze,
        y: int,
        theme: Theme,
        path_cells: PathCells,
    ) -> str:
        """Dibuja una fila de celdas con sus muros verticales."""
        parts: list[str] = []
        for x in range(maze.width):
            cell = maze.get_cell(x, y)
            west = "|" if cell.has_wall(Direction.WEST) else " "
            parts.append(self._paint(west, theme.wall))
            symbol, color = self._symbol(
                maze,
                x,
                y,
                theme,
                path_cells,
            )
            if color is None:
                parts.append(symbol)
            else:
                parts.append(self._paint(symbol, color))
            if x == maze.width - 1:
                east = "|" if cell.has_wall(Direction.EAST) else " "
                parts.append(self._paint(east, theme.wall))
        return "".join(parts)

    def _symbol(
        self,
        maze: Maze,
        x: int,
        y: int,
        theme: Theme,
        path_cells: PathCells,
    ) -> tuple[str, int | None]:
        """Devuelve el contenido de una celda y su color."""
        position = (x, y)
        if position == maze.entry:
            return " S ", theme.entry
        if position == maze.exit:
            return " E ", theme.exit
        if position in maze.pattern42_cells:
            return "###", theme.pattern
        if position in path_cells:
            return " * ", theme.path
        return " " * CELL_WIDTH, None

    def _paint(self, text: str, color: int) -> str:
        """Aplica color ANSI si está habilitado."""
        return paint(text, color, self.use_color)
