"""Tests for the public maze generator."""

from __future__ import annotations

import pytest

from mazegen import Direction, MazeError, MazeGenerator
from mazegen.pattern42 import GLYPH_ROWS
from tests.helpers import (
    assert_border_closed,
    assert_coherent_walls,
    normalized_pattern,
    path_positions,
)

ALGORITHMS = ("recursive_backtracker", "hunt_and_kill")


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("perfect", [True, False])
def test_generated_maze_is_structurally_valid(
    algorithm: str,
    perfect: bool,
) -> None:
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=perfect,
        seed=42,
        algorithm=algorithm,
    )
    maze = generator.generate()
    assert maze.width == 20
    assert maze.height == 15
    assert maze.is_fully_connected()
    assert not maze.has_open_3x3()
    assert_coherent_walls(maze)
    assert_border_closed(maze)
    assert path_positions(maze, generator.solve())[-1] == maze.exit


def test_seed_is_reproducible() -> None:
    first = MazeGenerator(20, 15, (0, 0), (19, 14), seed=123)
    second = MazeGenerator(20, 15, (0, 0), (19, 14), seed=123)
    assert first.generate().to_hex_rows() == second.generate().to_hex_rows()
    assert first.solve() == second.solve()


def test_different_seeds_produce_different_mazes() -> None:
    first = MazeGenerator(20, 15, (0, 0), (19, 14), seed=1).generate()
    second = MazeGenerator(20, 15, (0, 0), (19, 14), seed=2).generate()
    assert first.to_hex_rows() != second.to_hex_rows()


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_perfect_mode_has_no_loops(algorithm: str) -> None:
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=True,
        seed=42,
        algorithm=algorithm,
    )
    maze = generator.generate()
    assert maze.count_loops() == 0
    assert maze.is_fully_connected()


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_playable_mode_is_pacman_ready(algorithm: str) -> None:
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=False,
        seed=42,
        algorithm=algorithm,
    )
    maze = generator.generate()
    region = maze.region(maze.entry)
    corners = {
        (0, 0),
        (19, 0),
        (0, 14),
        (19, 14),
    }
    centre = {(9, 7), (10, 7)}
    assert maze.count_loops() >= 2
    assert not maze.real_dead_end_cells()
    assert corners <= region
    assert centre & region
    assert not maze.has_open_3x3()


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_pattern42_shape_and_closed_cells(algorithm: str) -> None:
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=False,
        seed=42,
        algorithm=algorithm,
    )
    maze = generator.generate()
    assert generator.pattern42_present is True
    glyph = normalized_pattern(maze)
    assert glyph == GLYPH_ROWS
    assert maze.entry not in maze.pattern42_cells
    assert maze.exit not in maze.pattern42_cells
    for position in maze.pattern42_cells:
        assert maze.get_cell(*position).is_fully_closed()


def test_pattern42_is_omitted_when_too_small() -> None:
    generator = MazeGenerator(
        8,
        6,
        (0, 0),
        (7, 5),
        perfect=True,
        seed=42,
    )
    maze = generator.generate()
    assert not maze.pattern42_cells
    assert generator.pattern42_present is False
    assert generator.last_warning is not None
    assert "42" in generator.last_warning
    assert maze.is_fully_connected()


def test_pattern42_can_be_disabled() -> None:
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=True,
        seed=42,
        pattern42=False,
    )
    maze = generator.generate()
    assert not maze.pattern42_cells
    assert generator.pattern42_present is False
    assert generator.last_warning is None


@pytest.mark.parametrize(
    ("width", "height", "entry", "exit_position", "algorithm"),
    [
        (0, 5, (0, 0), (0, 1), "recursive_backtracker"),
        (5, 0, (0, 0), (0, 1), "recursive_backtracker"),
        (5, 5, (5, 0), (0, 1), "recursive_backtracker"),
        (5, 5, (0, 0), (0, 0), "recursive_backtracker"),
        (5, 5, (0, 0), (4, 4), "unknown"),
    ],
)
def test_invalid_parameters_raise(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_position: tuple[int, int],
    algorithm: str,
) -> None:
    with pytest.raises(MazeError):
        MazeGenerator(
            width,
            height,
            entry,
            exit_position,
            algorithm=algorithm,
        )


def test_boolean_dimensions_are_rejected() -> None:
    with pytest.raises(MazeError):
        MazeGenerator(True, 5, (0, 0), (0, 1))
    with pytest.raises(MazeError):
        MazeGenerator(5, False, (0, 0), (0, 1))


def test_get_maze_and_solve_require_generation() -> None:
    generator = MazeGenerator(5, 5, (0, 0), (4, 4))
    with pytest.raises(MazeError):
        generator.get_maze()
    with pytest.raises(MazeError):
        generator.solve()


def test_generated_maze_has_external_walls() -> None:
    module = MazeGenerator(9, 7, (0, 0), (8, 6), seed=5)
    maze = module.generate()
    for x in range(9):
        assert maze.has_wall(x, 0, Direction.NORTH)
        assert maze.has_wall(x, 6, Direction.SOUTH)
    for y in range(7):
        assert maze.has_wall(0, y, Direction.WEST)
        assert maze.has_wall(8, y, Direction.EAST)



"""
test_generator.py
│   ├── seed reproducible
│   ├── diferentes seeds
│   └── solución
"""


def test_reproducible_seed():
    pass


def test_diferents_seeds():
    pass


def test_solution():
    pass


def test_generator():
    test_reproducible_seed()
    test_diferents_seeds()
    test_solution()


if __name__ == "__main__":
    try:
        test_generator()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting...")
    except BaseException as base_err:
        print(f"{base_err.__class__.__name__}: {base_err}\n")
