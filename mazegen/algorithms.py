from __future__ import annotations
import random
from .model import CARDINAL_DIRECTIONS, Direction, Maze, MazeError

WallCandidate = tuple[int, int, Direction]
Neighbor = tuple[Direction, tuple[int, int]]
SUPPORTED_ALGORITHMS: tuple[str, ...] = ("dfs", "hunt_and_kill")


class BaseAlgorithm:
    def __init__(self, maze: Maze, rng: random.Random, start: tuple[int, int] | None) -> None:
        self.maze = maze
        self.rng = rng
        self.start = start
        self.visited: set[tuple[int, int]] = set()

    def generate(self) -> None:
        """Método principal que lanza el algoritmo (Fachada)."""
        self._carve()

    def _carve(self) -> None:
        raise NotImplementedError

    """
    def _remove_dead_ends(self) -> None:
        for _ in range(3):
            dead_ends = self.maze.real_dead_end_cells()
            if not dead_ends:
                return
            self.rng.shuffle(dead_ends)
            progress = False
            for x, y in dead_ends:
                if len(self.maze.open_neighbors(x, y)) != 1:
                    continue
                directions = list(CARDINAL_DIRECTIONS)
                self.rng.shuffle(directions)
                for direction in directions:
                    neighbor = self.maze.get_neighbor(x, y, direction)
                    if neighbor is None:
                        continue
                    if neighbor in self.maze.pattern42_cells:
                        continue
                    if not self.maze.has_wall(x, y, direction):
                        continue
                    if not self.maze.open_wall(x, y, direction):
                        continue
                    if self.maze.has_open_3x3():
                        self.maze.close_wall(x, y, direction)
                        continue
                    progress = True
                    break
            if not progress:
                return
    
    
    def _wall_candidates(self) -> list[WallCandidate]:
        candidates: list[WallCandidate] = []
        for x, y in self.maze.non_pattern_cells():
            for direction in (Direction.EAST, Direction.SOUTH):
                neighbor = self.maze.get_neighbor(x, y, direction)
                if neighbor is None:
                    continue
                if neighbor in self.maze.pattern42_cells:
                    continue
                if not self.maze.has_wall(x, y, direction):
                    continue
                candidates.append((x, y, direction))
        return candidates
    

    
    def _add_one_cycle(self) -> bool:
        candidates = self._wall_candidates()
        self.rng.shuffle(candidates)
        for x, y, direction in candidates:
            if not self.maze.open_wall(x, y, direction):
                continue
            if self.maze.has_open_3x3():
                self.maze.close_wall(x, y, direction)
                continue
            return True
        return False
    """

    def _search_square(self, x: int, y: int) -> bool:
        for c in range(y, y + 2):
            for l in range(x, x + 2):
                cell = self.maze.get_cell(l, c)
                if cell.has_wall(Direction.EAST) or cell.has_wall(Direction.SOUTH):
                    return True
        return False

    def _makes_3_square(self, x: int, y: int, direction: Direction) -> bool:
        neighbor = self.maze.get_neighbor(x, y, direction)
        if neighbor is None:
            return False
        nx, ny = neighbor

        if not self.maze.open_wall(x, y, direction):
            return False

        min_x = max(0, min(x, nx) - 2)
        min_y = max(0, min(y, ny) - 2)
        max_x = min(self.maze.width - 3, max(x, nx))
        max_y = min(self.maze.height - 3, max(y, ny))

        creates = False
        for sy in range(min_y, max_y + 1):
            for sx in range(min_x, max_x + 1):
                if not self._search_square(sx, sy):
                    creates = True
                    break
            if creates:
                break

        self.maze.close_wall(x, y, direction)
        return creates

    def braid(self, p_break: float = 0.35) -> None:
        """Lógica del usuario para hacer el laberinto jugable rompiendo muros (35%)."""
        #warnings: list[str] = []

        for cy in range(self.maze.height):
            for cx in range(self.maze.width):
                if (cx, cy) in self.maze.pattern42_cells:
                    continue

                if self.rng.random() < p_break:
                    directions = list(CARDINAL_DIRECTIONS)
                    direction = self.rng.choice(directions)
                    neighbor = self.maze.get_neighbor(cx, cy, direction)

                    if neighbor is None or neighbor in self.maze.pattern42_cells:
                        continue

                    if self.maze.has_wall(cx, cy, direction) and not self._makes_3_square(cx, cy, direction):
                        self.maze.open_wall(cx, cy, direction)

    """
    def braid(self, target_loops: int = 3) -> list[str]:
        Turn a perfect maze into a playable board.
        warnings: list[str] = []
        self._remove_dead_ends()
        loops = self.maze.count_loops()
        attempts = 0
        max_attempts = max(4, len(self.maze.non_pattern_cells()))
        while loops < target_loops and attempts < max_attempts:
            attempts += 1
            if not self._add_one_cycle():
                break
            loops = self.maze.count_loops()

        if loops < 2:
            warnings.append(
                "No se pudieron crear al menos dos rutas independientes; "
                "el tablero es demasiado pequeño."
            )
        dead_ends = len(self.maze.real_dead_end_cells())
        if dead_ends > 2:
            warnings.append(
                f"Quedan {dead_ends} callejones sin salida; el máximo "
                "recomendado es 2."
            )
        return warnings
    """

    def _resolve_start(self) -> tuple[int, int]:
        candidate = self.maze.entry if self.start is None else self.start
        if (
            self.maze.is_inside(*candidate)
            and candidate not in self.maze.pattern42_cells
        ):
            return candidate
        cells = self.maze.non_pattern_cells()
        if not cells:
            raise MazeError(
                "No hay celdas libres para generar el laberinto."
            )
        return cells[0]
            

class DFS(BaseAlgorithm):
    def _carve(self) -> None:
        """Generador DFS del usuario."""
        current = self._resolve_start()
        self.visited = {current}
        stack: list[tuple[int, int]] = [current]
        
        while stack:
            x, y = stack[-1]
            directions = list(CARDINAL_DIRECTIONS)
            self.rng.shuffle(directions)
            
            moved = False
            for direction in directions:
                neighbor = self.maze.get_neighbor(x, y, direction)

                if neighbor is None or neighbor in self.maze.pattern42_cells:
                    continue

                if neighbor in self.visited:
                    continue
                    
                self.maze.open_wall(x, y, direction)
                self.visited.add(neighbor)
                stack.append(neighbor)
                moved = True
                break
                
            if not moved:
                stack.pop()


class HuntAndKill(BaseAlgorithm):
    def _unvisited_neighbors(self, position: tuple[int, int]) -> list[Neighbor]:
        x, y = position
        result: list[Neighbor] = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.maze.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.maze.pattern42_cells:
                continue
            if neighbor in self.visited:
                continue
            result.append((direction, neighbor))
        return result

    def _visited_neighbors(self, position: tuple[int, int]) -> list[Neighbor]:
        x, y = position
        result: list[Neighbor] = []
        for direction in CARDINAL_DIRECTIONS:
            neighbor = self.maze.get_neighbor(x, y, direction)
            if neighbor is None:
                continue
            if neighbor in self.maze.pattern42_cells:
                continue
            if neighbor in self.visited:
                result.append((direction, neighbor))
        return result

    def _hunt(self) -> tuple[int, int] | None:
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                position = (x, y)
                if position in self.visited:
                    continue
                if position in self.maze.pattern42_cells:
                    continue
                candidates = self._visited_neighbors(position)
                if not candidates:
                    continue
                direction, _ = self.rng.choice(candidates)
                self.maze.open_wall(x, y, direction)
                self.visited.add(position)
                return position
        return None

    def _carve(self) -> None:
        """Carve a perfect maze with the hunt-and-kill algorithm."""
        current = self._resolve_start()
        self.visited = {current}
        while True:
            candidates = self._unvisited_neighbors(current)
            if candidates:
                direction, neighbor = self.rng.choice(candidates)
                self.maze.open_wall(current[0], current[1], direction)
                self.visited.add(neighbor)
                current = neighbor
                continue
            hunted = self._hunt()
            if hunted is None:
                return
            current = hunted


class AlgorithmFactory:
    @classmethod
    def get_algorithm(cls, maze: Maze, algorithm: str, rng: random.Random, start: tuple[int, int] | None) -> BaseAlgorithm:
        if algorithm == "dfs":
            return DFS(maze, rng, start)
        if algorithm == "hunt_and_kill":
            return HuntAndKill(maze, rng, start)
        raise MazeError(
            f"Algoritmo desconocido: {algorithm!r}. "
            f"Use uno de: {', '.join(SUPPORTED_ALGORITHMS)}."
        )