import random
import unittest

from .algorithms import (
    AlgorithmFactory,
    BaseAlgorithm,
    DFS,
    HuntAndKill,
)
from .model import Direction, Maze, MazeError
from .pattern42 import Pattern42Placer


def render_simple_ascii(maze: Maze) -> str:
    """Renderizado ASCII clásico sencillo mediante guiones y barras."""
    lines = []
    lines.append("+" + "---+" * maze.width)

    for y in range(maze.height):
        row_str = "|"
        bottom_str = "+"
        for x in range(maze.width):
            cell = maze.get_cell(x, y)

            # Contenido de la celda
            if (x, y) in maze.pattern42_cells:
                body = "42 "
            elif (x, y) == maze.entry:
                body = " E "
            elif (x, y) == maze.exit:
                body = " X "
            else:
                body = "   "

            # Muro Este
            east = "|" if cell.has_wall(Direction.EAST) else " "
            row_str += body + east

            # Muro Sur
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
        self.width = 41
        self.height = 34
        self.entry = (0, 0)
        self.exit = (40, 33)
        self.rng = random.Random()

    def test_dfs_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = DFS(maze, self.rng, start=self.entry)
        algo.generate()
        algo.braid()
        print_maze(maze, "DFS con Logo (11x9)")

        self.assertTrue(maze.is_fully_connected())
        self.assertEqual(len(algo.visited), len(maze.non_pattern_cells()))


class TestHuntAndKill(unittest.TestCase):

    def setUp(self) -> None:
        self.width = 20
        self.height = 14
        self.entry = (0, 0)
        self.exit = (19, 13)
        self.rng = random.Random(42)

    def test_hunt_and_kill_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = HuntAndKill(maze, self.rng, start=self.entry)
        algo.generate()

        print_maze(maze, "Hunt & Kill con Logo (11x9)")

        self.assertTrue(maze.is_fully_connected())
        self.assertEqual(len(algo.visited), len(maze.non_pattern_cells()))

    def test_hunt_and_kill_braid_with_logo(self) -> None:
        maze = create_maze_with_logo(self.width, self.height, self.entry, self.exit)
        algo = HuntAndKill(maze, self.rng, start=self.entry)
        algo.generate()
        algo.braid(p_break=0.3)

        print_maze(maze, "Hunt & Kill con Logo + Braid (Jugable)")

        self.assertGreater(maze.count_loops(), 0)


if __name__ == "__main__":
    unittest.main()