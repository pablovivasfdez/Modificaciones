"""Tests for the reusable maze model."""

from __future__ import annotations

import pytest

from mazegen import Direction, Maze, MazeError
from mazegen.model import ALL_WALLS, Cell


def test_new_cell_has_all_walls() -> None:
    cell = Cell()
    assert cell.walls == ALL_WALLS
    assert cell.has_wall(Direction.NORTH)
    assert cell.has_wall(Direction.EAST)
    assert cell.has_wall(Direction.SOUTH)
    assert cell.has_wall(Direction.WEST)


def test_cell_open_and_close_wall() -> None:
    cell = Cell()
    cell.remove_wall(Direction.NORTH)
    assert not cell.has_wall(Direction.NORTH)
    assert cell.has_wall(Direction.EAST)
    cell.add_wall(Direction.NORTH)
    assert cell.has_wall(Direction.NORTH)
    assert cell.to_hex() == "F"


def test_direction_delta_and_opposite() -> None:
    assert Direction.NORTH.delta == (0, -1)
    assert Direction.EAST.delta == (1, 0)
    assert Direction.SOUTH.delta == (0, 1)
    assert Direction.WEST.delta == (-1, 0)
    assert Direction.NORTH.opposite == Direction.SOUTH
    assert Direction.SOUTH.opposite == Direction.NORTH
    assert Direction.EAST.opposite == Direction.WEST
    assert Direction.WEST.opposite == Direction.EAST


def test_maze_dimensions_and_cells() -> None:
    maze = Maze(4, 3)
    assert maze.width == 4
    assert maze.height == 3
    assert len(maze.grid) == 3
    assert len(maze.grid[0]) == 4
    assert list(maze.cells())[0] == (0, 0)
    assert list(maze.cells())[-1] == (3, 2)


def test_coordinates_and_neighbors() -> None:
    maze = Maze(4, 3)
    assert maze.is_inside(0, 0)
    assert maze.is_inside(3, 2)
    assert not maze.is_inside(-1, 0)
    assert not maze.is_inside(4, 0)
    assert maze.get_neighbor(1, 1, Direction.NORTH) == (1, 0)
    assert maze.get_neighbor(1, 1, Direction.EAST) == (2, 1)
    assert maze.get_neighbor(1, 1, Direction.SOUTH) == (1, 2)
    assert maze.get_neighbor(1, 1, Direction.WEST) == (0, 1)
    assert maze.get_neighbor(0, 0, Direction.NORTH) is None


def test_get_cell_outside_maze() -> None:
    maze = Maze(4, 3)
    with pytest.raises(IndexError):
        maze.get_cell(4, 0)
    with pytest.raises(IndexError):
        maze.get_cell(0, 3)


def test_open_and_close_walls_are_coherent() -> None:
    maze = Maze(3, 2)
    assert maze.open_wall(0, 0, Direction.EAST)
    assert not maze.has_wall(0, 0, Direction.EAST)
    assert not maze.has_wall(1, 0, Direction.WEST)
    assert maze.close_wall(0, 0, Direction.EAST)
    assert maze.has_wall(0, 0, Direction.EAST)
    assert maze.has_wall(1, 0, Direction.WEST)


def test_border_walls_cannot_be_opened() -> None:
    maze = Maze(2, 2)
    assert not maze.open_wall(0, 0, Direction.NORTH)
    assert not maze.open_wall(0, 0, Direction.WEST)
    assert not maze.open_wall(1, 1, Direction.EAST)
    assert not maze.open_wall(1, 1, Direction.SOUTH)


def test_pattern_cells_are_closed_and_protected() -> None:
    maze = Maze(
        3,
        3,
        entry=(0, 0),
        exit=(2, 2),
        pattern42_cells=[(1, 1)],
    )
    assert maze.get_cell(1, 1).is_fully_closed()
    assert not maze.open_wall(0, 1, Direction.EAST)
    assert maze.has_wall(0, 1, Direction.EAST)


def test_hex_rows() -> None:
    maze = Maze(2, 2)
    rows = maze.to_hex_rows()
    assert rows == ["FF", "FF"]
    assert all(len(row) == 2 for row in rows)


def test_count_loops_on_a_tree() -> None:
    maze = Maze(2, 1, entry=(0, 0), exit=(1, 0))
    assert maze.open_wall(0, 0, Direction.EAST)
    assert maze.count_passages() == 1
    assert maze.count_loops() == 0
    assert maze.is_fully_connected()


def test_count_loops_with_an_extra_edge() -> None:
    maze = Maze(2, 2, entry=(0, 0), exit=(1, 1))
    assert maze.open_wall(0, 0, Direction.EAST)
    assert maze.open_wall(1, 0, Direction.SOUTH)
    assert maze.open_wall(0, 1, Direction.EAST)
    assert maze.open_wall(0, 0, Direction.SOUTH)
    assert maze.count_loops() == 1


def test_has_open_3x3() -> None:
    maze = Maze(3, 3)
    for y in range(3):
        for x in range(2):
            maze.open_wall(x, y, Direction.EAST)
    for y in range(2):
        for x in range(3):
            maze.open_wall(x, y, Direction.SOUTH)
    assert maze.has_open_3x3()


def test_small_open_block_is_allowed() -> None:
    maze = Maze(3, 2)
    for y in range(2):
        for x in range(2):
            maze.open_wall(x, y, Direction.EAST)
    for x in range(2):
        maze.open_wall(x, 0, Direction.SOUTH)
    assert not maze.has_open_3x3()


def test_invalid_layouts() -> None:
    with pytest.raises(MazeError):
        Maze(0, 1)
    with pytest.raises(MazeError):
        Maze(1, 1, entry=(0, 0), exit=(0, 0))
    with pytest.raises(MazeError):
        Maze(1, 1, entry=(2, 0), exit=(0, 0))


def test_real_and_enclosed_dead_ends() -> None:
    maze = Maze(
        3,
        3,
        entry=(0, 0),
        exit=(2, 2),
        pattern42_cells=[(1, 1)],
    )
    maze.open_wall(0, 0, Direction.EAST)
    maze.open_wall(1, 0, Direction.SOUTH)
    maze.open_wall(1, 1, Direction.EAST)
    maze.open_wall(2, 1, Direction.SOUTH)
    real = maze.real_dead_end_cells()
    enclosed = maze.enclosed_dead_end_cells()
    assert isinstance(real, list)
    assert isinstance(enclosed, list)


"""
test_maze.py
│   ├── dimensiones
│   ├── conectividad
│   ├── paredes coherentes
│   ├── entry/exit
│   ├── PERFECT=True
│   └── PERFECT=False
"""
import pytest
from core.Maze import Maze
from core.MazeCell import Cell
from core.MazeDirections import MazeDirection


def test_new_cell_has_all_walls() -> None:
    """A new cell must start completely closed."""
    cell = Cell()
    assert cell.walls == 0xF
    assert cell.has_wall(MazeDirection.NORTH)
    assert cell.has_wall(MazeDirection.EAST)
    assert cell.has_wall(MazeDirection.SOUTH)
    assert cell.has_wall(MazeDirection.WEST)


def test_cell_open_and_close_wall() -> None:
    """A cell must be able to open and close individual walls."""
    cell = Cell()
    cell.remove_wall(MazeDirection.NORTH)
    assert not cell.has_wall(MazeDirection.NORTH)
    assert cell.has_wall(MazeDirection.EAST)
    assert cell.has_wall(MazeDirection.SOUTH)
    assert cell.has_wall(MazeDirection.WEST)
    cell.add_wall(MazeDirection.NORTH)
    assert cell.has_wall(MazeDirection.NORTH)


def test_maze_dimensions() -> None:
    """Maze dimensions must match the requested size."""
    maze = Maze(4, 3)
    assert maze.width == 4
    assert maze.height == 3
    assert len(maze.grid) == 3
    assert len(maze.grid[0]) == 4


def test_coordinates_inside_maze() -> None:
    """Coordinate validation must work correctly."""
    maze = Maze(4, 3)
    assert maze.is_inside(0, 0)
    assert maze.is_inside(3, 2)
    assert not maze.is_inside(-1, 0)
    assert not maze.is_inside(4, 0)
    assert not maze.is_inside(0, -1)
    assert not maze.is_inside(0, 3)


def test_get_cell() -> None:
    """get_cell must return the requested cell."""
    maze = Maze(4, 3)
    cell = maze.get_cell(2, 1)
    assert isinstance(cell, Cell)


def test_get_cell_outside_maze() -> None:
    """get_cell must reject invalid coordinates."""
    maze = Maze(4, 3)
    with pytest.raises(IndexError):
        maze.get_cell(4, 0)
    with pytest.raises(IndexError):
        maze.get_cell(0, 3)


def test_get_neighbor() -> None:
    """Neighbours must have the correct coordinates."""
    maze = Maze(4, 3)
    assert maze.get_neighbor(1, 1, MazeDirection.NORTH) == (1, 0)
    assert maze.get_neighbor(1, 1, MazeDirection.EAST) == (2, 1)
    assert maze.get_neighbor(1, 1, MazeDirection.SOUTH) == (1, 2)
    assert maze.get_neighbor(1, 1, MazeDirection.WEST) == (0, 1)


def test_no_neighbor_outside_maze() -> None:
    """Border cells must have no neighbour outside the maze."""
    maze = Maze(4, 3)
    assert maze.get_neighbor(0, 0, MazeDirection.NORTH) is None
    assert maze.get_neighbor(0, 0, MazeDirection.WEST) is None
    assert maze.get_neighbor(3, 2, MazeDirection.EAST) is None
    assert maze.get_neighbor(3, 2, MazeDirection.SOUTH) is None


def test_open_wall_updates_both_cells() -> None:
    """Opening a wall must update both sides of the connection."""
    maze = Maze(3, 3)
    maze.open_wall(1, 1, MazeDirection.EAST)
    assert not maze.has_wall(1, 1, MazeDirection.EAST)
    assert not maze.has_wall(2, 1, MazeDirection.WEST)


def test_open_wall_preserves_other_walls() -> None:
    """Opening one wall must not modify unrelated walls."""
    maze = Maze(3, 3)
    maze.open_wall(1, 1, MazeDirection.EAST)
    cell = maze.get_cell(1, 1)
    assert cell.has_wall(MazeDirection.NORTH)
    assert cell.has_wall(MazeDirection.SOUTH)
    assert cell.has_wall(MazeDirection.WEST)
    assert not cell.has_wall(MazeDirection.EAST)


def test_open_border_wall_fails() -> None:
    """Opening a wall outside the maze must fail."""
    maze = Maze(3, 3)
    result = maze.open_wall(0, 0, MazeDirection.WEST)
    assert result is False
    assert maze.has_wall(0, 0, MazeDirection.WEST)


def test_close_wall_updates_both_cells() -> None:
    """Closing a connection must close both matching walls."""
    maze = Maze(3, 3)
    maze.open_wall(1, 1, MazeDirection.EAST)
    maze.close_wall(1, 1, MazeDirection.EAST)
    assert maze.has_wall(1, 1, MazeDirection.EAST)
    assert maze.has_wall(2, 1, MazeDirection.WEST)


def test_hex_representation() -> None:
    """Wall masks must convert to hexadecimal correctly."""
    cell = Cell()
    assert cell.to_hex() == "F"
    cell.remove_wall(MazeDirection.NORTH)
    assert cell.to_hex() == "E"
    cell.remove_wall(MazeDirection.EAST)
    assert cell.to_hex() == "C"
    cell.remove_wall(MazeDirection.SOUTH)
    assert cell.to_hex() == "8"
    cell.remove_wall(MazeDirection.WEST)
    assert cell.to_hex() == "0"


def test_hex_grid() -> None:
    """The complete maze must be exportable row by row."""
    maze = Maze(2, 2)
    assert maze.to_hex_grid() == [
        "FF",
        "FF",
    ]


def test_fully_closed_cell() -> None:
    """A new cell must be fully closed."""
    cell = Cell()
    assert cell.is_fully_closed()
    cell.remove_wall(MazeDirection.NORTH)
    assert not cell.is_fully_closed()


def test_visited_state() -> None:
    """Visited state must be independently controllable."""
    maze = Maze(2, 2)
    assert not maze.get_cell(0, 0).visited
    maze.mark_visited(0, 0)
    assert maze.get_cell(0, 0).visited
    maze.reset_visited()
    assert not maze.get_cell(0, 0).visited


def test_invalid_maze_dimensions() -> None:
    """Maze dimensions must be positive."""
    with pytest.raises(ValueError):
        Maze(0, 5)
    with pytest.raises(ValueError):
        Maze(5, 0)
    with pytest.raises(ValueError):
        Maze(-1, 5)
    with pytest.raises(ValueError):
        Maze(5, -1)
