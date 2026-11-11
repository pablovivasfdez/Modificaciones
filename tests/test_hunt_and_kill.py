"""Focused tests for the hunt-and-kill algorithm."""

from __future__ import annotations

from mazegen import MazeGenerator
from tests.helpers import (
    assert_border_closed,
    assert_coherent_walls,
    path_positions,
)


def test_hunt_and_kill_perfect_maze() -> None:
    generator = MazeGenerator(
        25,
        18,
        (0, 0),
        (24, 17),
        perfect=True,
        seed=99,
        algorithm="hunt_and_kill",
    )
    maze = generator.generate()
    assert maze.is_fully_connected()
    assert maze.count_loops() == 0
    assert not maze.has_open_3x3()
    assert_coherent_walls(maze)
    assert_border_closed(maze)
    path_positions(maze, generator.solve())


def test_hunt_and_kill_playable_maze() -> None:
    generator = MazeGenerator(
        25,
        18,
        (0, 0),
        (24, 17),
        perfect=False,
        seed=99,
        algorithm="hunt_and_kill",
    )
    maze = generator.generate()
    assert maze.is_fully_connected()
    assert maze.count_loops() >= 2
    assert not maze.real_dead_end_cells()
    assert not maze.has_open_3x3()
    path_positions(maze, generator.solve())


def test_algorithm_changes_maze_structure() -> None:
    first = MazeGenerator(
        25,
        18,
        (0, 0),
        (24, 17),
        seed=99,
        algorithm="recursive_backtracker",
    ).generate()
    second = MazeGenerator(
        25,
        18,
        (0, 0),
        (24, 17),
        seed=99,
        algorithm="hunt_and_kill",
    ).generate()
    assert first.to_hex_rows() != second.to_hex_rows()



"""Tests para los generadores de laberintos (hunt_and_kill y bfs).

Todos los tests se ejecutan contra cada generador de GENERATORS. Para
añadir otro algoritmo, importalo y anadelo al diccionario.

Ejecutar desde la raiz del proyecto:
    python tests/test_hunt_and_kill.py
o con pytest:
    python -m pytest tests/ -v
"""
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from mazegen.hunt_and_kill import hunt_and_kill  # noqa: E402
from mazegen.bfs import bfs as bfs_generator  # noqa: E402

GENERATORS = {
    "hunt_and_kill": hunt_and_kill,
    "bfs": bfs_generator,
}

BIT = {"N": 1, "E": 2, "S": 4, "W": 8}
OPPOSITE = {"N": "S", "S": "N", "E": "W", "W": "E"}
DELTA = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}

SIZES = [(1, 1), (1, 5), (5, 1), (2, 2), (5, 5), (10, 7), (30, 20)]


def is_open(grid, x, y, d):
    """True si la celda (x, y) tiene el muro d abierto (bit a 0)."""
    return not (grid[y][x] & BIT[d])


def count_edges(grid, width, height):
    """Cuenta pasillos (cada uno una sola vez: solo mirando E y S)."""
    edges = 0
    for y in range(height):
        for x in range(width):
            if is_open(grid, x, y, "E"):
                edges += 1
            if is_open(grid, x, y, "S"):
                edges += 1
    return edges


def reachable(grid, width, height, start=(0, 0)):
    """BFS de referencia siguiendo solo muros abiertos."""
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and is_open(grid, x, y, d) and (nx, ny) not in seen):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def print_maze(grid, width, height):
    """Dibuja el laberinto en ASCII para inspeccionarlo a ojo."""
    out = ["+" + "---+" * width]
    for y in range(height):
        row, below = "|", "+"
        for x in range(width):
            row += "   " + ("|" if grid[y][x] & BIT["E"] else " ")
            below += ("---" if grid[y][x] & BIT["S"] else "   ") + "+"
        out += [row, below]
    print("\n".join(out))


def test_dimensions():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            grid = gen(w, h, (0, 0), 42)
            assert len(grid) == h, f"{name} {w}x{h}: alto incorrecto"
            assert all(len(r) == w for r in grid), \
                f"{name} {w}x{h}: ancho incorrecto"


def test_cell_values_valid():
    for name, gen in GENERATORS.items():
        grid = gen(10, 10, (0, 0), 1)
        assert all(0 <= c <= 15 for row in grid for c in row), \
            f"{name}: valores fuera de 0-15"


def test_borders_closed():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            grid = gen(w, h, (0, 0), 7)
            for x in range(w):
                assert grid[0][x] & BIT["N"], f"{name} {w}x{h}: borde N abierto x={x}"
                assert grid[h - 1][x] & BIT["S"], f"{name} {w}x{h}: borde S abierto x={x}"
            for y in range(h):
                assert grid[y][0] & BIT["W"], f"{name} {w}x{h}: borde W abierto y={y}"
                assert grid[y][w - 1] & BIT["E"], f"{name} {w}x{h}: borde E abierto y={y}"


def test_walls_symmetric():
    """Si A tiene abierto el muro hacia B, B debe tenerlo abierto hacia A."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            grid = gen(w, h, (0, 0), 3)
            for y in range(h):
                for x in range(w):
                    for d, (dx, dy) in DELTA.items():
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < w and 0 <= ny < h:
                            assert is_open(grid, x, y, d) == \
                                is_open(grid, nx, ny, OPPOSITE[d]), \
                                f"{name} {w}x{h}: muro incoherente ({x},{y}) {d}"


def test_all_cells_reachable():
    """Sin zonas aisladas: desde (0,0) se llega a todas las celdas."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            for seed in range(20):
                grid = gen(w, h, (0, 0), seed)
                assert len(reachable(grid, w, h)) == w * h, \
                    f"{name} {w}x{h} seed={seed}: hay celdas aisladas"


def test_perfect_maze_no_cycles():
    """Laberinto perfecto = arbol: exactamente w*h - 1 pasillos."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            for seed in range(20):
                grid = gen(w, h, (0, 0), seed)
                assert count_edges(grid, w, h) == w * h - 1, \
                    f"{name} {w}x{h} seed={seed}: hay ciclos o faltan pasillos"


def test_no_closed_cells():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            if w * h == 1:
                continue
            grid = gen(w, h, (0, 0), 5)
            assert all(c != 15 for row in grid for c in row), \
                f"{name} {w}x{h}: hay celdas con los 4 muros"


def test_reproducible_same_seed():
    for name, gen in GENERATORS.items():
        assert gen(15, 15, (0, 0), 1234) == gen(15, 15, (0, 0), 1234), \
            f"{name}: misma seed, distinto laberinto"


def test_different_seeds_differ():
    for name, gen in GENERATORS.items():
        assert gen(15, 15, (0, 0), 1) != gen(15, 15, (0, 0), 2), \
            f"{name}: seeds distintas, mismo laberinto"


def test_start_not_in_corner():
    for name, gen in GENERATORS.items():
        for start in [(2, 3), (4, 4), (9, 6)]:
            grid = gen(10, 7, start, 11)
            assert len(reachable(grid, 10, 7)) == 70, \
                f"{name} start={start}: celdas aisladas"
            assert count_edges(grid, 10, 7) == 69, \
                f"{name} start={start}: no es perfecto"


def test_seed_none_works():
    for name, gen in GENERATORS.items():
        grid = gen(8, 8, (0, 0), 42)
        assert len(reachable(grid, 8, 8)) == 64, f"{name}: seed=None falla"


if __name__ == "__main__":
    tests = [(n, f) for n, f in sorted(globals().items())
             if n.startswith("test_") and callable(f)]
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"OK    {name}")
        except Exception as e:  # noqa: BLE001
            failed += 1
            print(f"FAIL  {name}: {type(e).__name__}: {e}")
    print(f"\n{len(tests) - failed}/{len(tests)} tests pasados\n")
    seed = int(sys.argv[1]) if len(sys.argv) > 1 else 42
    for gname, gen in GENERATORS.items():
        try:
            print(f"{gname} 8x5, seed {seed}:")
            print_maze(gen(8, 5, (0, 0), 42), 8, 5)
        except Exception as e:  # noqa: BLE001
            print(f"  no se pudo generar: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)