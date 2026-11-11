"""Public maze generator façade."""

from __future__ import annotations

import random

from .algorithms import AlgorithmFactory, SUPPORTED_ALGORITHMS
from .model import Maze, MazeError
from .pattern42 import Pattern42Placer
from .solver import shortest_path


class MazeGenerator:
    """Generate perfect mazes and playable Pac-Man style boards."""

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        perfect: bool = False,
        seed: int | None = None,
        algorithm: str = "dfs",
        pattern42: bool = True,
    ) -> None:
        #No creo que haga falta un pydantic y a chuparla
        self._validate_arguments(
            width,
            height,
            entry,
            exit,
            seed,
            algorithm,
        )
        self.width: int = width
        self.height: int = height
        self.entry: tuple[int, int] = entry
        self.exit: tuple[int, int] = exit
        self.perfect: bool = perfect
        self.algorithm: str = algorithm
        self.pattern42_present: bool = False
        self.last_warning: str | None = None
        self._pattern42_enabled: bool = pattern42
        self._seed: int = (
            random.SystemRandom().randint(0, 2**32 - 1)
            if seed is None
            else seed
        )
        self._maze: Maze | None = None

#tmpc se ssi hace falta, python o pydantic lo pueden cubrir ya
    @staticmethod
    def _validate_position(
        name: str,
        value: tuple[int, int],
    ) -> None:
        if len(value) != 2:
            raise MazeError(
                f"La {name} debe ser una tupla (x, y)."
            )
        x, y = value
        if not isinstance(x, int) or not isinstance(y, int):
            raise MazeError(
                f"Las coordenadas de la {name} deben ser enteros."
            )
        if isinstance(x, bool) or isinstance(y, bool):
            raise MazeError(
                f"Las coordenadas de la {name} deben ser enteros."
            )

#creo que no es util, ya lo cubre el parse
    def _validate_arguments(
        self,
        width: int,
        height: int,
        entry: tuple[int, int],
        exit: tuple[int, int],
        seed: int | None,
        algorithm: str,
    ) -> None:
        if not isinstance(width, int) or isinstance(width, bool):
            raise MazeError("WIDTH debe ser un número entero.")
        if not isinstance(height, int) or isinstance(height, bool):
            raise MazeError("HEIGHT debe ser un número entero.")
        if width <= 0 or height <= 0:
            raise MazeError(
                "WIDTH y HEIGHT deben ser mayores que cero."
            )
        if seed is not None and (
            not isinstance(seed, int) or isinstance(seed, bool)
        ):
            raise MazeError("La seed debe ser un número entero o None.")
        if algorithm not in SUPPORTED_ALGORITHMS:
            supported = ", ".join(SUPPORTED_ALGORITHMS)
            raise MazeError(
                f"Algoritmo desconocido: {algorithm!r}. "
                f"Use uno de: {supported}."
            )
        self._validate_position("entrada", entry)
        self._validate_position("salida", exit)
        for name, position in (
            ("entrada", entry),
            ("salida", exit),
        ):
            x, y = position
            if not (0 <= x < width and 0 <= y < height):
                raise MazeError(
                    f"La {name} {position} está fuera del laberinto."
                )
        if entry == exit:
            raise MazeError(
                "La entrada y la salida deben ocupar celdas distintas."
            )

    @property
    def seed(self) -> int:
        """Return the effective seed used by this generator."""
        return self._seed

    def generate(self) -> Maze:
        """Generate a maze and return it."""
        placement = Pattern42Placer.place(
            self.width,
            self.height,
            self.entry,
            self.exit,
            self._pattern42_enabled,
        )
        warnings: list[str] = []
        if placement.warning is not None:
            warnings.append(placement.warning)
        if self.entry in placement.cells:
            raise MazeError(
                "La entrada no puede formar parte del patrón 42."
            )
        if self.exit in placement.cells:
            raise MazeError(
                "La salida no puede formar parte del patrón 42."
            )

        maze = Maze(
            self.width,
            self.height,
            self.entry,
            self.exit,
            placement.cells,
        )
        rng = random.Random(self._seed)
        algo = AlgorithmFactory.get_algorithm(maze, self.algorithm, rng, self.entry)
        algo.generate()
        if not self.perfect:
            warnings.extend(algo.braid())
        maze.reset_visited()
        self._validate_maze(maze)

        self._maze = maze
        self.pattern42_present = placement.present
        self.last_warning = " | ".join(warnings) if warnings else None
        return maze

    def _validate_maze(self, maze: Maze) -> None:
        if not maze.is_fully_connected():
            raise MazeError(
                "La generación produjo celdas no conectadas fuera del "
                "patrón 42."
            )
        if maze.has_open_3x3():
            raise MazeError(
                "La generación produjo una zona abierta de 3x3."
            )
        for position in maze.pattern42_cells:
            if not maze.get_cell(*position).is_fully_closed():
                raise MazeError(
                    "El patrón 42 contiene una celda que no está "
                    "totalmente cerrada."
                )
        if self.perfect and maze.count_loops() != 0:
            raise MazeError(
                "El laberinto perfecto contiene ciclos no permitidos."
            )

    def get_maze(self) -> Maze:
        """Return the generated maze."""
        if self._maze is None:
            raise MazeError(
                "Todavía no se ha generado ningún laberinto."
            )
        return self._maze

    def solve(self) -> str:
        """Return the shortest path from entry to exit."""
        if self._maze is None:
            raise MazeError(
                "Todavía no se ha generado ningún laberinto."
            )
        return shortest_path(self._maze)
