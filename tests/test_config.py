"""Tests for the configuration parser and validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.config import ConfigError, MazeConfig
from tests.helpers import write_config

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "config.txt"

VALID = """\
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=output/maze.txt
PERFECT=False
"""


def test_default_config_is_valid() -> None:
    config = MazeConfig.from_file(DEFAULT_CONFIG)
    assert config.width == 20
    assert config.height == 15
    assert config.entry == (0, 0)
    assert config.exit == (19, 14)
    assert config.perfect is False
    assert config.seed == 42
    assert config.algorithm == "recursive_backtracker"
    assert config.theme == "midnight"
    assert config.renderer == "terminal"


def test_case_insensitive_keys_and_values(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "config.txt",
        """\
        width=11
        height=9
        entry=1,2
        exit=10,8
        output_file=out/maze.txt
        perfect=TRUE
        seed=7
        algorithm=HUNT_AND_KILL
        theme=ARCTIC
        renderer=TERMINAL
        """,
    )
    config = MazeConfig.from_file(path)
    assert config.width == 11
    assert config.height == 9
    assert config.entry == (1, 2)
    assert config.exit == (10, 8)
    assert config.perfect is True
    assert config.seed == 7
    assert config.algorithm == "hunt_and_kill"
    assert config.theme == "arctic"
    assert config.renderer == "terminal"


def test_comments_and_blank_lines(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "config.txt",
        """\
        # Comentario completo
        WIDTH=10  # comentario al final
        HEIGHT=8

        ENTRY=0,0
        EXIT=9,7
        OUTPUT_FILE=out.txt # otro comentario
        PERFECT=True
        """,
    )
    config = MazeConfig.from_file(path)
    assert config.width == 10
    assert config.output_file == "out.txt"


def test_bom_and_crlf_are_supported(tmp_path: Path) -> None:
    path = tmp_path / "config.txt"
    path.write_bytes(b"\xef\xbb\xbf" + VALID.replace("\n", "\r\n").encode())
    config = MazeConfig.from_file(path)
    assert config.width == 20


def test_missing_mandatory_key(tmp_path: Path) -> None:
    path = write_config(
        tmp_path / "config.txt",
        VALID.replace("WIDTH=20\n", ""),
    )
    with pytest.raises(ConfigError, match="WIDTH"):
        MazeConfig.from_file(path)


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="No se encontró"):
        MazeConfig.from_file(tmp_path / "missing.txt")


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("WIDTH 20\n", "falta el carácter '='"),
        ("WIDTH=20=30\n", "exactamente un '='"),
        ("WIDTH=\n", "no puede estar vacío"),
        ("WIDTH=20\nWIDTH=21\n", "duplicada"),
        ("UNKNOWN=1\n", "clave desconocida"),
        ("\n", "Faltan claves obligatorias"),
    ],
)
def test_syntax_errors(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    path = write_config(tmp_path / "config.txt", content)
    with pytest.raises(ConfigError, match=message):
        MazeConfig.from_file(path)


@pytest.mark.parametrize(
    ("content", "message"),
    [
        (VALID.replace("WIDTH=20", "WIDTH=abc"), "WIDTH debe ser"),
        (VALID.replace("WIDTH=20", "WIDTH=0"), "mayor que cero"),
        (VALID.replace("HEIGHT=15", "HEIGHT=-1"), "mayor que cero"),
        (VALID.replace("ENTRY=0,0", "ENTRY=1,2,3"), "formato x,y"),
        (VALID.replace("ENTRY=0,0", "ENTRY=a,b"), "números enteros"),
        (VALID.replace("ENTRY=0,0", "ENTRY=20,0"), "fuera del laberinto"),
        (VALID.replace("EXIT=19,14", "EXIT=19,15"), "fuera del laberinto"),
        (VALID.replace("EXIT=19,14", "EXIT=0,0"), "celdas distintas"),
        (VALID.replace("PERFECT=False", "PERFECT=yes"), "true o false"),
        (VALID.replace("PERFECT=False", "PERFECT=False\nSEED=x"), "entero"),
        (
            VALID.replace(
                "PERFECT=False",
                "PERFECT=False\nALGORITHM=unknown",
            ),
            "ALGORITHM no válido",
        ),
        (
            VALID.replace(
                "PERFECT=False",
                "PERFECT=False\nTHEME=unknown",
            ),
            "THEME no válido",
        ),
        (
            VALID.replace(
                "PERFECT=False",
                "PERFECT=False\nRENDERER=mlx",
            ),
            "RENDERER no válido",
        ),
    ],
)
def test_semantic_errors(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    path = write_config(tmp_path / "config.txt", content)
    with pytest.raises(ConfigError, match=message):
        MazeConfig.from_file(path)



"""
test_config.py
│   ├── configuración válida
│   ├── configuración incompleta
│   ├── valores inválidos
│   └── coordenadas inválidas
"""