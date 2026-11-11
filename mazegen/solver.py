"""Shortest-path solver for a :class:`mazegen.model.Maze`."""

from __future__ import annotations

from collections import deque

from .model import CARDINAL_DIRECTIONS, Direction, Maze, MazeError

LETTERS: dict[Direction, str] = {
    Direction.NORTH: "N",
    Direction.EAST: "E",
    Direction.SOUTH: "S",
    Direction.WEST: "W",
}

Parent = tuple[tuple[int, int], str] | None
Position = tuple[int, int]


def shortest_path(
    maze: Maze,
    start: Position | None = None,
    goal: Position | None = None,
) -> str:
    """Return the shortest path between two cells as ``N/E/S/W`` letters.

    Neighbours are explored in the deterministic order North, East,
    South, West.  Cells belonging to the ``42`` pattern are never
    traversed.

    Args:
        maze: Maze to solve.
        start: Optional start cell; the maze entry is used by default.
        goal: Optional goal cell; the maze exit is used by default.

    Returns:
        The movement letters from start to goal.

    Raises:
        MazeError: If the start, goal or a matching path is invalid.
    """
    origin = maze.entry if start is None else start
    destination = maze.exit if goal is None else goal
    for name, position in (
        ("inicio", origin),
        ("destino", destination),
    ):
        if not maze.is_inside(*position):
            raise MazeError(
                f"El {name} {position} está fuera del laberinto."
            )
        if position in maze.pattern42_cells:
            raise MazeError(
                f"El {name} {position} pertenece al patrón 42."
            )

    parents: dict[Position, Parent] = {origin: None}
    pending: deque[Position] = deque([origin])
    while pending:
        current = pending.popleft()
        if current == destination:
            break
        for direction in CARDINAL_DIRECTIONS:
            neighbor = maze.get_neighbor(
                current[0],
                current[1],
                direction,
            )
            if neighbor is None:
                continue
            if neighbor in maze.pattern42_cells:
                continue
            if neighbor in parents:
                continue
            if maze.has_wall(current[0], current[1], direction):
                continue
            parents[neighbor] = (current, LETTERS[direction])
            pending.append(neighbor)

    if destination not in parents:
        raise MazeError(
            "No existe un camino entre la entrada y la salida."
        )

    steps: list[str] = []
    node = destination
    while node != origin:
        parent = parents[node]
        if parent is None:
            raise MazeError(
                "No se pudo reconstruir el camino más corto."
            )
        previous, letter = parent
        steps.append(letter)
        node = previous
    steps.reverse()
    return "".join(steps)
