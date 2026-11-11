"""Reusable maze generation package.

The public API is intentionally small: one generator class plus the
model types needed to inspect and export the resulting maze.
"""

from .generator import MazeGenerator
from .model import Cell, Direction, Maze, MazeError

__all__ = [
    "MazeGenerator",
    "Maze",
    "Cell",
    "Direction",
    "MazeError",
]

__version__ = "1.0.0"
