"""Integration tests against the official maze analyzer."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from app.output import write_maze
from mazegen import MazeGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ANALYZER = PROJECT_ROOT / "maze_analyzer.py"


def run_analyzer(
    output_file: Path,
    *extra: str,
) -> subprocess.CompletedProcess[str]:
    """Run the analyzer and return its completed process."""
    return subprocess.run(
        [sys.executable, str(ANALYZER), str(output_file), *extra],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def build_output(tmp_path: Path, perfect: bool) -> Path:
    """Generate a maze and write it to a temporary output file."""
    generator = MazeGenerator(
        20,
        15,
        (0, 0),
        (19, 14),
        perfect=perfect,
        seed=42,
    )
    maze = generator.generate()
    return write_maze(
        maze,
        generator.solve(),
        tmp_path / "maze.txt",
    )


def test_analyzer_accepts_perfect_maze(tmp_path: Path) -> None:
    output = build_output(tmp_path, perfect=True)
    result = run_analyzer(output)
    assert result.returncode == 0
    assert "Wall coherence   : OK" in result.stdout
    assert "PERFECT maze" in result.stdout


def test_analyzer_accepts_pacman_maze(tmp_path: Path) -> None:
    output = build_output(tmp_path, perfect=False)
    result = run_analyzer(output)
    assert result.returncode == 0
    assert "Wall coherence   : OK" in result.stdout
    assert "Pac-Man-USABLE" in result.stdout
    assert "0 real" in result.stdout


def test_analyzer_returns_zero_for_negative_verdict(
    tmp_path: Path,
) -> None:
    output = build_output(tmp_path, perfect=False)
    result = run_analyzer(output, "--min-loops", "100")
    assert result.returncode == 0
    assert "Not Pac-Man-ready" in result.stdout


def test_analyzer_rejects_malformed_file(tmp_path: Path) -> None:
    malformed = tmp_path / "malformed.txt"
    malformed.write_text("XYZ\n", encoding="utf-8")
    result = run_analyzer(malformed)
    assert result.returncode != 0
    assert "Malformed maze file" in result.stdout
