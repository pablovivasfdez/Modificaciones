"""Legacy import path kept as a thin wrapper over :mod:`mazegen`."""

from .Maze import Cell, Maze, MazeError
from .MazeCell import MazeCell
from .MazeDirections import Direction, MazeDirection

__all__ = [
    "Cell",
    "Direction",
    "Maze",
    "MazeCell",
    "MazeDirection",
    "MazeError",
]
