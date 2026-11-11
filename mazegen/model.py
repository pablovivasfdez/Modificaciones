"""Core data structures for the reusable ``mazegen`` package.

The module is intentionally self-contained.  It only depends on the
Python standard library and never imports modules from the application
that consumes the package.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntFlag
from typing import Iterable, Iterator

ALL_WALLS: int = 0xF


class MazeError(Exception):
    """Raised when a maze cannot be built, generated or solved."""


class Direction(IntFlag):
    """Cardinal directions and their wall bits.

    The integer value is the bit used by the hexadecimal wall encoding:
    North is the least significant bit and West the most significant one.
    """

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def delta(self) -> tuple[int, int]:
        """Return the ``(dx, dy)`` offset for this direction."""
        if self == Direction.NORTH:
            return (0, -1)
        if self == Direction.EAST:
            return (1, 0)
        if self == Direction.SOUTH:
            return (0, 1)
        if self == Direction.WEST:
            return (-1, 0)
        raise MazeError(f"Dirección no válida: {self!r}")

    @property
    def opposite(self) -> Direction:
        """Return the direction seen from the neighbouring cell."""
        if self == Direction.NORTH:
            return Direction.SOUTH
        if self == Direction.EAST:
            return Direction.WEST
        if self == Direction.SOUTH:
            return Direction.NORTH
        if self == Direction.WEST:
            return Direction.EAST
        raise MazeError(f"Dirección no válida: {self!r}")


CARDINAL_DIRECTIONS: tuple[Direction, ...] = (
    Direction.NORTH,
    Direction.EAST,
    Direction.SOUTH,
    Direction.WEST,
)


@dataclass
class Cell:
    """A single maze cell.

    Attributes:
        walls: Bit mask where a set bit means a closed wall.
        visited: Generic visit marker available to package users.
    """

    walls: int = ALL_WALLS
    visited: bool = False

    def has_wall(self, direction: Direction) -> bool:
        """Return whether the wall in ``direction`` is closed."""
        return bool(self.walls & int(direction))

    def add_wall(self, direction: Direction) -> None:
        """Close the wall in ``direction``."""
        self.walls |= int(direction)

    def remove_wall(self, direction: Direction) -> None:
        """Open the wall in ``direction``."""
        self.walls &= ~int(direction)

    def is_fully_closed(self) -> bool:
        """Return whether the four walls are closed."""
        return self.walls == ALL_WALLS

    def to_hex(self) -> str:
        """Return the wall mask as one uppercase hexadecimal digit."""
        return format(self.walls, "X")


class Maze:
    """Rectangular maze grid with coherent walls on both sides.

    Args:
        width: Number of cells in the horizontal axis.
        height: Number of cells in the vertical axis.
        entry: Entry coordinates as ``(x, y)``.
        exit: Exit coordinates as ``(x, y)``.
        pattern42_cells: Coordinates that must remain fully closed.

    Raises:
        MazeError: If the dimensions, entry, exit or pattern are invalid.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int] | None = None,
        exit: tuple[int, int] | None = None,
        pattern42_cells: Iterable[tuple[int, int]] | None = None,
    ) -> None:
        if width <= 0 or height <= 0:
            raise MazeError(
                "Las dimensiones del laberinto deben ser positivas."
            )
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = (
            entry if entry is not None else (0, 0)
        )
        self.exit: tuple[int, int] = (
            exit if exit is not None else (width - 1, height - 1)
        )
        self.pattern42_cells: set[tuple[int, int]] = set(
            pattern42_cells or ()
        )
        self.grid: list[list[Cell]] = [
            [Cell() for _ in range(width)] for _ in range(height)
        ]
        #protege el logo entrada y salida
        self._validate_layout()
        for position in self.pattern42_cells:
            self.get_cell(*position).walls = ALL_WALLS

    @property
    def pattern42(self) -> set[tuple[int, int]]:
        """Alias for :attr:`pattern42_cells`."""
        return self.pattern42_cells

    def _validate_layout(self) -> None:
        for name, position in (
            ("entrada", self.entry),
            ("salida", self.exit),
        ):
            x, y = position
            if not self.is_inside(x, y):
                raise MazeError(
                    f"La {name} {position} está fuera del laberinto."
                )
        if self.entry == self.exit:
            raise MazeError(
                "La entrada y la salida deben ocupar celdas distintas."
            )
        for position in self.pattern42_cells:
            x, y = position
            if not self.is_inside(x, y):
                raise MazeError(
                    f"La celda 42 {position} está fuera del laberinto."
                )
            if position in (self.entry, self.exit):
                raise MazeError(
                    "La entrada y la salida no pueden formar parte del "
                    "patrón 42."
                )

    def is_inside(self, x: int, y: int) -> bool:
        """Return whether the coordinates are inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> Cell:
        """Return the cell at ``(x, y)``.

        Raises:
            IndexError: If the coordinates are outside the maze.
        """
        if not self.is_inside(x, y):
            raise IndexError(
                f"Las coordenadas ({x}, {y}) están fuera del laberinto."
            )
        return self.grid[y][x]

#OJOJOJO
    def get_neighbor(
        self,
        x: int,
        y: int,
        direction: Direction,
    ) -> tuple[int, int] | None:
        """Return the neighbouring coordinates, or ``None`` at the border."""
        dx, dy = direction.delta
        neighbor_x = x + dx
        neighbor_y = y + dy
        if not self.is_inside(neighbor_x, neighbor_y):
            return None
        return neighbor_x, neighbor_y

    def open_wall(
        self,
        x: int,
        y: int,
        direction: Direction,
    ) -> bool:
        """Open a wall and the matching wall of the neighbouring cell.

        Cells that belong to the ``42`` pattern can never be opened.

        Returns:
            ``True`` if a valid passage was opened, otherwise ``False``.
        """
        self.get_cell(x, y)
        neighbor = self.get_neighbor(x, y, direction)
        if neighbor is None:
            return False
        if (x, y) in self.pattern42_cells:
            return False
        if neighbor in self.pattern42_cells:
            return False
        neighbor_x, neighbor_y = neighbor
        self.get_cell(x, y).remove_wall(direction)
        self.get_cell(neighbor_x, neighbor_y).remove_wall(
            direction.opposite
        )
        return True

    def close_wall(
        self,
        x: int,
        y: int,
        direction: Direction,
    ) -> bool:
        """Close a wall and the matching wall of the neighbouring cell.

        Returns:
            ``True`` if a valid wall was closed, otherwise ``False``.
        """
        cell = self.get_cell(x, y)
        neighbor = self.get_neighbor(x, y, direction)
        if neighbor is None:
            return False
        neighbor_x, neighbor_y = neighbor
        cell.add_wall(direction)
        self.get_cell(neighbor_x, neighbor_y).add_wall(
            direction.opposite
        )
        return True

    def has_wall(
        self,
        x: int,
        y: int,
        direction: Direction,
    ) -> bool:
        """Return whether the cell at ``(x, y)`` has that wall closed."""
        return self.get_cell(x, y).has_wall(direction)

    def mark_visited(self, x: int, y: int) -> None:
        """Mark the cell at ``(x, y)`` as visited."""
        self.get_cell(x, y).visited = True

    def reset_visited(self) -> None:
        """Clear the visited flag of every cell."""
        for row in self.grid:
            for cell in row:
                cell.visited = False

#OJOJOJOJO
    def non_pattern_cells(self) -> list[tuple[int, int]]:
        """Return every walkable coordinate, excluding the ``42`` cells."""
        return [
            (x, y)
            for x, y in self.cells()
            if (x, y) not in self.pattern42_cells
        ]

#   APARTIIR D EAQUI MRIAR SI TIENEN USO O NO
    def cells(self) -> Iterator[tuple[int, int]]:
        """Yield every cell coordinate in row-major order."""
        for y in range(self.height):
            for x in range(self.width):
                yield x, y

#braid de la IA
    def open_neighbors(
        self,
        x: int,
        y: int,
    ) -> list[tuple[int, int]]:
        """Return neighbours reachable through open passages."""
        if (x, y) in self.pattern42_cells:
            return []
        result: list[tuple[int, int]] = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.pattern42_cells:
                continue
            neighbor_x, neighbor_y = neighbor
            if self.has_wall(x, y, direction):
                continue
            if self.has_wall(
                neighbor_x,
                neighbor_y,
                direction.opposite,
            ):
                continue
            result.append(neighbor)
        return result
#OJOJOJOJO
#para el chequer de haber visitadas todas
    def region(
        self,
        start: tuple[int, int] | None = None,
    ) -> set[tuple[int, int]]:
        """Return every cell connected to ``start`` through passages."""
        origin = self.entry if start is None else start
        self.get_cell(*origin)
        seen: set[tuple[int, int]] = {origin}
        pending: list[tuple[int, int]] = [origin]
        while pending:
            current = pending.pop()
            for neighbor in self.open_neighbors(*current):
                if neighbor not in seen:
                    seen.add(neighbor)
                    pending.append(neighbor)
        return seen

#basante util, chequea que se accedio a todas las celdas(tmpc le veo sentido ya que en teoria el algoritmo las mira todas)
    def is_fully_connected(self) -> bool:
        """Return whether every non-``42`` cell belongs to one region."""
        target = set(self.non_pattern_cells())
        if not target:
            return True
        return self.region(self.entry) == target
#braid de la IA

#OJOJOJOJJO
    def count_passages(self) -> int:
        """Return the number of open passages between adjacent cells."""
        total = 0
        for x, y in self.non_pattern_cells():
            for direction in (Direction.EAST, Direction.SOUTH):
                neighbor = self.get_neighbor(x, y, direction)
                if neighbor is None:
                    continue
                if neighbor in self.pattern42_cells:
                    continue
                neighbor_x, neighbor_y = neighbor
                if self.has_wall(x, y, direction):
                    continue
                if self.has_wall(
                    neighbor_x,
                    neighbor_y,
                    direction.opposite,
                ):
                    continue
                total += 1
        return total

#OJOJOJO
#braid de la IA
    def count_loops(self) -> int:
        """Return the number of independent cycles in the walkable graph."""
        cells = self.non_pattern_cells()
        if not cells:
            return 0
        remaining = set(cells)
        components = 0
        while remaining:
            start = remaining.pop()
            component = self.region(start)
            remaining.difference_update(component)
            components += 1
        return self.count_passages() - len(cells) + components

#braid de la IA
    def dead_end_cells(self) -> list[tuple[int, int]]:
        """Return walkable cells with exactly one open passage.

        This includes cells enclosed by the ``42`` pattern.  Use
        :meth:`real_dead_end_cells` to count only the ones that could
        still be connected to another normal cell.
        """
        return [
            (x, y)
            for x, y in self.non_pattern_cells()
            if len(self.open_neighbors(x, y)) == 1
        ]

#braid de la IA
    def _has_openable_wall(self, x: int, y: int) -> bool:
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.pattern42_cells:
                continue
            if self.has_wall(x, y, direction):
                return True
        return False

#braid de la IA
    def real_dead_end_cells(self) -> list[tuple[int, int]]:
        """Return dead ends with at least one wall openable to a cell."""
        return [
            (x, y)
            for x, y in self.dead_end_cells()
            if self._has_openable_wall(x, y)
        ]

#braid de la IA
    def enclosed_dead_end_cells(self) -> list[tuple[int, int]]:
        """Return dead ends surrounded only by the border or ``42`` cells."""
        real = set(self.real_dead_end_cells())
        return [
            cell for cell in self.dead_end_cells() if cell not in real
        ]

#braid de la IA
    def has_open_3x3(self) -> bool:
        """Return whether the maze contains a fully open ``3x3`` area."""
        for top in range(self.height - 2):
            for left in range(self.width - 2):
                if self._is_open_block(left, top):
                    return True
        return False

#braid de la IA
    def _is_open_block(self, left: int, top: int) -> bool:
        for y in range(top, top + 3):
            for x in range(left, left + 3):
                cell = self.get_cell(x, y)
                if x < left + 2 and cell.has_wall(Direction.EAST):
                    return False
                if y < top + 2 and cell.has_wall(Direction.SOUTH):
                    return False
        return True

    def to_hex_rows(self) -> list[str]:
        """Return one hexadecimal string per maze row."""
        return [
            "".join(cell.to_hex() for cell in row)
            for row in self.grid
        ]

    def to_hex_grid(self) -> list[str]:
        """Alias for :meth:`to_hex_rows` kept for convenience."""
        return self.to_hex_rows()
