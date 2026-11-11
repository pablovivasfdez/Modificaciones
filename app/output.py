"""Escritura del fichero de salida con el formato del subject."""

from __future__ import annotations

from pathlib import Path

from mazegen import Maze


def build_output(maze: Maze, solution: str) -> str:
    """Construye el contenido exacto del fichero de salida.

    El formato es: una fila hexadecimal por cada fila del laberinto,
    una línea vacía, la entrada, la salida y el camino más corto.
    """
    rows = maze.to_hex_rows()
    entry_x, entry_y = maze.entry
    exit_x, exit_y = maze.exit
    lines = [
        *rows,
        "",
        f"{entry_x},{entry_y}",
        f"{exit_x},{exit_y}",
        solution,
    ]
    return "\n".join(lines) + "\n"


def write_maze(
    maze: Maze,
    solution: str,
    output_file: str | Path,
) -> Path:
    """Escribe el laberinto y devuelve la ruta final.

    Crea el directorio padre si no existe y usa ``\n`` como fin de
    línea en todas las plataformas.
    """
    path = Path(output_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    content = build_output(maze, solution)
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    return path
