"""Tests for the terminal application layer."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

import a_maze_ing
from app.controller import (
    MazeController,
    generate_maze,
    menu_available,
)
from app.menu import Menu
from app.renderers.console import ConsoleRenderer
from tests.helpers import make_config, write_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_console_renderer_shows_symbols() -> None:
    config = make_config(Path("."), width=20, height=15)
    generated = generate_maze(config)
    renderer = ConsoleRenderer(use_color=False)
    text = renderer.render(generated.maze, show_path=False)
    assert "S" in text
    assert "E" in text
    assert "###" in text
    assert "+" in text
    assert "|" in text
    assert "*" not in text


def test_console_renderer_shows_path() -> None:
    config = make_config(Path("."), width=20, height=15)
    generated = generate_maze(config)
    renderer = ConsoleRenderer(use_color=False)
    text = renderer.render(
        generated.maze,
        show_path=True,
        path=generated.solution,
    )
    assert "*" in text


def test_controller_non_interactive_writes_output(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    output = io.StringIO()
    errors = io.StringIO()
    controller = MazeController(
        config,
        output_stream=output,
        error_stream=errors,
    )
    controller.run(interactive=False)
    assert (tmp_path / "maze.txt").exists()
    assert "S" in output.getvalue()
    assert errors.getvalue() == ""


def test_console_renderer_changes_theme_colours() -> None:
    config = make_config(Path("."), width=20, height=15)
    generated = generate_maze(config)
    first = ConsoleRenderer(use_color=True).render(
        generated.maze,
        theme_name="midnight",
    )
    second = ConsoleRenderer(use_color=True).render(
        generated.maze,
        theme_name="obsidian",
    )
    assert "\x1b[" in first
    assert first != second


def test_controller_menu_cycles_through_actions(tmp_path: Path) -> None:
    config = make_config(tmp_path)
    input_stream = io.StringIO("2\n3\n4\n1\n5\n")
    output = io.StringIO()
    controller = MazeController(
        config,
        input_stream=input_stream,
        output_stream=output,
        error_stream=io.StringIO(),
    )
    controller.generate()
    controller.write_output()
    before = (tmp_path / "maze.txt").read_bytes()
    controller.run(interactive=True)
    after = (tmp_path / "maze.txt").read_bytes()
    assert (tmp_path / "maze.txt").exists()
    assert "hunt_and_kill" in output.getvalue()
    assert before != after


def test_menu_rejects_invalid_choices() -> None:
    input_stream = io.StringIO("x\n9\n5\n")
    output = io.StringIO()
    menu = Menu(input_stream, output)
    assert menu.prompt("midnight", "recursive_backtracker", False) == 5
    assert "Opción no válida" in output.getvalue()


def test_menu_stops_on_closed_input() -> None:
    menu = Menu(io.StringIO(""), io.StringIO())
    assert menu.prompt("midnight", "recursive_backtracker", False) is None


class FakeTTY(io.StringIO):
    """Input stream that pretends to be an interactive terminal."""

    def isatty(self) -> bool:
        return True


def test_menu_availability(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("AMAZEING_NO_MENU", raising=False)
    assert menu_available(FakeTTY()) is True
    monkeypatch.setenv("AMAZEING_NO_MENU", "1")
    assert menu_available(FakeTTY()) is False


def test_main_rejects_extra_arguments(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert a_maze_ing.main(["a.txt", "b.txt"]) == 1
    assert "Uso:" in capsys.readouterr().err


def test_main_reports_invalid_config(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    config = write_config(
        tmp_path / "bad.txt",
        "WIDTH=10\nHEIGHT=10\n",
    )
    assert a_maze_ing.main([str(config)]) == 1
    assert "Error de configuración" in capsys.readouterr().err


def test_main_uses_default_config_from_any_directory(
    tmp_path: Path,
) -> None:
    environment = os.environ.copy()
    environment["AMAZEING_NO_MENU"] = "1"
    result = subprocess.run(
        [sys.executable, str(PROJECT_ROOT / "a_maze_ing.py")],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert (tmp_path / "output" / "maze.txt").exists()
    assert "Traceback" not in result.stderr


def test_main_accepts_one_config_argument(tmp_path: Path) -> None:
    config = write_config(
        tmp_path / "custom.txt",
        """\
WIDTH=9
HEIGHT=7
ENTRY=0,0
EXIT=8,6
OUTPUT_FILE=custom.txt
PERFECT=True
SEED=1
""",
    )
    environment = os.environ.copy()
    environment["AMAZEING_NO_MENU"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            str(PROJECT_ROOT / "a_maze_ing.py"),
            str(config),
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert (tmp_path / "custom.txt").exists()
    assert "Traceback" not in result.stderr
