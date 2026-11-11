"""Reusable assertions and builders for the test suite."""

from __future__ import annotations

from pathlib import Path

from app.config import MazeConfig
from mazegen import Direction, Maze
from mazegen.pattern42 import GLYPH_ROWS

STEP: dict[str, tuple[int, int]] = {
    "N": (0, -1),
    "E": (1, 0),
    "S": (0, 1),
    "W": (-1, 0),
}

LETTER_DIRECTION: dict[str, Direction] = {
    "N": Direction.NORTH,
    "E": Direction.EAST,
    "S": Direction.SOUTH,
    "W": Direction.WEST,
}


def write_config(path: Path, content: str) -> Path:
    """Write a configuration file and return its path."""
    path.write_text(content, encoding="utf-8")
    return path


def make_config(
    tmp_path: Path,
    *,
    width: int = 20,
    height: int = 15,
    entry: tuple[int, int] = (0, 0),
    exit_position: tuple[int, int] = (19, 14),
    output_file: str | None = None,
    perfect: bool = False,
    seed: int | None = 42,
    algorithm: str = "recursive_backtracker",
    theme: str = "midnight",
    renderer: str = "terminal",
) -> MazeConfig:
    """Build a valid configuration for tests."""
    output = (
        str(tmp_path / "maze.txt")
        if output_file is None
        else output_file
    )
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_position,
        output_file=output,
        perfect=perfect,
        seed=seed,
        algorithm=algorithm,
        theme=theme,
        renderer=renderer,
    )


def path_positions(maze: Maze, path: str) -> list[tuple[int, int]]:
    """Walk a ``N/E/S/W`` path and assert that it is valid.

    Returns:
        Every cell visited, including the entry and the exit.
    """
    x, y = maze.entry
    positions = [(x, y)]
    for letter in path:
        direction = LETTER_DIRECTION[letter]
        assert not maze.has_wall(x, y, direction), (
            f"El camino atraviesa un muro en ({x},{y}) hacia {letter}."
        )
        delta_x, delta_y = STEP[letter]
        x += delta_x
        y += delta_y
        assert maze.is_inside(x, y), "El camino sale del laberinto."
        positions.append((x, y))
    assert (x, y) == maze.exit, "El camino no termina en la salida."
    return positions


def assert_coherent_walls(maze: Maze) -> None:
    """Assert that every shared wall is encoded identically on both sides."""
    for y in range(maze.height):
        for x in range(maze.width):
            for direction in (Direction.EAST, Direction.SOUTH):
                neighbor = maze.get_neighbor(x, y, direction)
                if neighbor is None:
                    continue
                neighbor_x, neighbor_y = neighbor
                current = maze.has_wall(x, y, direction)
                opposite = maze.get_cell(
                    neighbor_x,
                    neighbor_y,
                ).has_wall(direction.opposite)
                assert current == opposite, (
                    f"Pared incoherente entre ({x},{y}) y "
                    f"({neighbor_x},{neighbor_y}) en {direction.name}."
                )


def assert_border_closed(maze: Maze) -> None:
    """Assert that the outer border is completely closed."""
    for x in range(maze.width):
        assert maze.has_wall(x, 0, Direction.NORTH)
        assert maze.has_wall(x, maze.height - 1, Direction.SOUTH)
    for y in range(maze.height):
        assert maze.has_wall(0, y, Direction.WEST)
        assert maze.has_wall(maze.width - 1, y, Direction.EAST)


def normalized_pattern(maze: Maze) -> tuple[str, ...] | None:
    """Return the pattern glyph normalized to its bounding box."""
    cells = maze.pattern42_cells
    if not cells:
        return None
    min_x = min(x for x, _ in cells)
    max_x = max(x for x, _ in cells)
    min_y = min(y for _, y in cells)
    max_y = max(y for _, y in cells)
    if max_x - min_x + 1 != len(GLYPH_ROWS[0]):
        return None
    if max_y - min_y + 1 != len(GLYPH_ROWS):
        return None
    return tuple(
        "".join(
            "1" if (min_x + column, min_y + row) in cells else "0"
            for column in range(len(GLYPH_ROWS[0]))
        )
        for row in range(len(GLYPH_ROWS))
    )
