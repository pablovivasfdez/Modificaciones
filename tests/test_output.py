"""Tests for the hexadecimal output writer."""

from __future__ import annotations

from pathlib import Path

from app.output import build_output, write_maze
from mazegen import Maze, MazeGenerator
from tests.helpers import path_positions


def make_generated() -> tuple[Maze, str]:
    """Build a deterministic maze and its solution."""
    generator = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    maze = generator.generate()
    return maze, generator.solve()


def test_build_output_format() -> None:
    maze, solution = make_generated()
    content = build_output(maze, solution)
    lines = content.split("\n")
    assert lines[-1] == ""
    assert lines[-2] == solution
    assert lines[-3] == "19,14"
    assert lines[-4] == "0,0"
    assert lines[15] == ""
    assert len(lines[:15]) == 15
    assert all(len(row) == 20 for row in lines[:15])
    assert all(
        character in "0123456789ABCDEF"
        for row in lines[:15]
        for character in row
    )


def test_output_path_is_written_with_newlines(tmp_path: Path) -> None:
    maze, solution = make_generated()
    path = write_maze(
        maze,
        solution,
        tmp_path / "nested" / "maze.txt",
    )
    data = path.read_bytes()
    assert data.endswith(b"\n")
    assert b"\r" not in data
    text = data.decode("utf-8")
    assert text.count("\n") == 19


def test_solution_is_the_shortest_path() -> None:
    maze, solution = make_generated()
    positions = path_positions(maze, solution)
    assert positions[0] == maze.entry
    assert positions[-1] == maze.exit
    assert set(solution) <= set("NESW")


def test_output_is_reproducible() -> None:
    first_maze, first_solution = make_generated()
    second_maze, second_solution = make_generated()
    assert build_output(
        first_maze,
        first_solution,
    ) == build_output(
        second_maze,
        second_solution,
    )
