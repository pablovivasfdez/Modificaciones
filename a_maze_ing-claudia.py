#!/usr/bin/env python3
"""Punto de entrada de la aplicación A-Maze-ing."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Sequence

from mazegen import MazeError

from app.config import ConfigError, MazeConfig
from app.controller import MazeController

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "config.txt"
USAGE = "Uso: python3 a_maze_ing.py [config.txt]"


def _config_path(arguments: Sequence[str]) -> Path:
    """Resuelve la ruta de configuración indicada por el usuario."""
    if not arguments:
        return DEFAULT_CONFIG
    return Path(arguments[0])


def main(argv: Sequence[str] | None = None) -> int:
    """Ejecuta la aplicación y devuelve el código de salida."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) > 1:
        print(USAGE, file=sys.stderr)
        return 1

    config_path = _config_path(arguments)
    try:
        maze_config = MazeConfig.from_file(config_path)
        amazeing_maze = Maze(maze_config)
        controller = MazeController(maze_config)
        controller.run()
    except ConfigError as error:
        print(f"Error de configuración: {error}", file=sys.stderr)
        return 1
    except MazeError as error:
        print(f"Error del laberinto: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Error de entrada/salida: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Error inesperado: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print(
            "\nEjecución interrumpida por el usuario.",
            file=sys.stderr,
        )
        return 1
    except BaseException as error:
        print(f"Error crítico: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
