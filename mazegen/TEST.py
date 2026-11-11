import random
import unittest

from .algorithms import (
    BFS,
    DFS,
    AlgorithmFactory,
    BaseAlgorithm,
    HuntAndKill,
)
from .model import CARDINAL_DIRECTIONS, Direction, Maze, MazeError
from .pattern42 import Pattern42Placer

LETTERS_TO_DIR: dict[str, Direction] = {
    "N": Direction.NORTH,
    "E": Direction.EAST,
    "S": Direction.SOUTH,
    "W": Direction.WEST,
}


def render_simple_ascii(maze: Maze) -> str:
    """Renderizado ASCII clásico sencillo mediante guiones y barras."""
    lines = []
    lines.append("+" + "---+" * maze.width)

    for y in range(maze.height):
        row_str = "|"
        bottom_str = "+"
        for x in range(maze.width):
            cell = maze.get_cell(x, y)

            if (x, y) in maze.pattern42_cells:
                body = "42 "
            elif (x, y) == maze.entry:
                body = " E "
            elif (x, y) == maze.exit:
                body = " X "
            else:
                body = "   "

            east = "|" if cell.has_wall(Direction.EAST) else " "
            row_str += body + east

            south = "---" if cell.has_wall(Direction.SOUTH) else "   "
            bottom_str += south + "+"

        lines.append(row_str)
        lines.append(bottom_str)

    return "\n".join(lines)


def print_maze(maze: Maze, title: str) -> None:
    print(f"\n--- {title} ---")
    print(render_simple_ascii(maze))
    print("-------------------\n")


def create_maze_with_logo(width: int = 11, height: int = 9, entry=(0, 0), exit=(10, 8)) -> Maze:
    """Crea una instancia de Maze incluyendo siempre el patrón 42."""
    placement = Pattern42Placer.place(width, height, entry, exit, enabled=True)
    return Maze(width, height, entry, exit, pattern42_cells=placement.cells)


def verify_path(maze: Maze, path_str: str, start: tuple[int, int], finish: tuple[int, int]) -> bool:
    """Verifica paso a paso que la cadena de solución (ej. NNEES) es válida y llega al destino."""
    curr_x, curr_y = start
    for char in path_str:
        if char not in LETTERS_TO_DIR:
            return False
        direction = LETTERS_TO_DIR[char]

        # Comprobar que no hay muro en esa dirección
        if maze.has_wall(curr_x, curr_y, direction):
            return False

        neighbor = maze.get_neighbor(curr_x, curr_y, direction)
        if neighbor is None or neighbor in maze.pattern42_cells:
            return False

        curr_x, curr_y = neighbor

    return (curr_x, curr_y) == finish


class TestAlgorithmFactory(unittest.TestCase):

    def setUp(self) -> None:
        self.maze = create_maze_with_logo(11, 9, (0, 0), (10, 8))
        self.rng = random.Random(42)

    def test_factory_creates_dfs(self) -> None:
        algo = AlgorithmFactory.get_algorithm(self.maze, "dfs", self.rng, start=(0, 0))
        self.assertIsInstance(algo, DFS)

    def test_factory_creates_hunt_and_kill(self) -> None:
        algo = AlgorithmFactory.get_algorithm(self.maze, "hunt_and_kill", self.rng, start=(0, 0))
        self.assertIsInstance(algo, HuntAndKill)

    def test_factory_raises_error_on_unknown_algorithm(self) -> None:
        with self.assertRaises(MazeError):
            AlgorithmFactory.get_algorithm(self.maze, "invalid", self.rng, start=(0, 0))


class TestBaseAlgorithm(unittest.TestCase):

    def setUp(self) -> None:
        self.maze = create_maze_with_logo(11, 9, (0, 0), (10, 8))
        self.rng = random.Random(123)

    def test_base_carve_raises_not_implemented(self) -> None:
        algo = BaseAlgorithm(self.maze, self.rng, start=(0, 0))
        with self.assertRaises(NotImplementedError):
            algo.generate()

    def test_resolve_start_valid_custom_position(self) -> None:
        algo = BaseAlgorithm(self.maze, self.rng, start=(2, 2))
        self.assertEqual(algo._resolve_start(), (2, 2))


class TestDFS(unittest.TestCase):

    def setUp(self) -> None:
        self.width = 11
        self.height = 9
        self.entry = (0, 0)
        self.exit = (10, 8)
        self.rng = random.Random(42)

    def test_dfs_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = DFS(maze, self.rng, start=self.entry)
        algo.generate()
        algo.braid()

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        solution = solver.solve()

        print(f"Solución BFS (DFS Maze): {solution}")
        print_maze(maze, f"DFS con Logo ({self.width}x{self.height})")

        self.assertTrue(maze.is_fully_connected())
        self.assertEqual(len(algo.visited), len(maze.non_pattern_cells()))
        self.assertTrue(verify_path(maze, solution, self.entry, self.exit))


class TestHuntAndKill(unittest.TestCase):

    def setUp(self) -> None:
        self.width = 11
        self.height = 9
        self.entry = (0, 0)
        self.exit = (10, 8)
        self.rng = random.Random(42)

    def test_hunt_and_kill_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = HuntAndKill(maze, self.rng, start=self.entry)
        algo.generate()

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        solution = solver.solve()

        print(f"Solución BFS (Hunt&Kill Maze): {solution}")
        print_maze(maze, f"Hunt & Kill con Logo ({self.width}x{self.height})")

        self.assertTrue(maze.is_fully_connected())
        self.assertEqual(len(algo.visited), len(maze.non_pattern_cells()))
        self.assertTrue(verify_path(maze, solution, self.entry, self.exit))

    def test_hunt_and_kill_braid_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = HuntAndKill(maze, self.rng, start=self.entry)
        algo.generate()
        algo.braid(p_break=0.3)

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        solution = solver.solve()

        print(f"Solución BFS (Braided Maze): {solution}")
        print_maze(maze, "Hunt & Kill con Logo + Braid (Jugable)")

        self.assertGreater(maze.count_loops(), 0)
        self.assertTrue(verify_path(maze, solution, self.entry, self.exit))


class TestBFS(unittest.TestCase):

    def setUp(self) -> None:
        self.width = 11
        self.height =  9
        self.entry = (0, 0)
        self.exit = (10, 8)
        self.rng = random.Random(99)

    def test_bfs_solves_dfs_maze(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        DFS(maze, self.rng, start=self.entry).generate()

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        solution = solver.solve()

        self.assertIsInstance(solution, str)
        self.assertGreater(len(solution), 0)
        self.assertTrue(verify_path(maze, solution, self.entry, self.exit))

    def test_bfs_solves_hunt_and_kill_maze(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        HuntAndKill(maze, self.rng, start=self.entry).generate()

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        solution = solver.solve()

        self.assertIsInstance(solution, str)
        self.assertGreater(len(solution), 0)
        self.assertTrue(verify_path(maze, solution, self.entry, self.exit))

    def test_bfs_raises_error_when_no_path(self) -> None:
        """Comprueba que BFS lanza MazeError si la salida queda incomunicada."""
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        DFS(maze, self.rng, start=self.entry).generate()

        # Cerramos todos los muros alrededor de la salida (10, 8)
        ex, ey = self.exit
        for direction in CARDINAL_DIRECTIONS:
            maze.close_wall(ex, ey, direction)

        solver = BFS(maze, self.rng, start=self.entry, finish=self.exit)
        with self.assertRaises(MazeError):
            solver.solve()


if __name__ == "__main__":
    unittest.main()
