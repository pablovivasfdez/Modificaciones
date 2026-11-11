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

SIZES = [(7, 7), (10, 7), (15, 15), (30, 20)]  # Tamaños adaptados al logo mínimo (requiere al menos 7x5)


def get_logo(height: int, width: int) -> list[tuple[int, int]]:
    if (height < 7 or width < 9): return None
    middlex, middley = width // 2 - 1, height // 2 - 1
    if (width % 2 != 0): middlex += 1
    if (height % 2 != 0): middley += 1
    values = []
    logo_positions = [
        (-1, 0), (-2, 0), (-3, 0), (-3, -1), (-3, -2), (-1, 1), (-1, 2),
        (1, 0), (2, 0), (3, 0), (3, -1), (3, - 2), (2, -2), (1, -2),
        (1, 1), (1, 2), (2, 2), (3, 2)
    ]
    for dx, dy in logo_positions:
        x = middlex + dx
        y = middley + dy
        if (0 <= x < width and 0 <= y < height):
            values.append((x, y))
    return values



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


def reachable(grid, width, height, start=(0, 0), logo=None):
    """BFS de referencia siguiendo solo muros abiertos, ignorando el logo."""
    logo_set = set(logo) if logo else set()
    seen = {start} | logo_set
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for d, (dx, dy) in DELTA.items():
            nx, ny = x + dx, y + dy
            if (0 <= nx < width and 0 <= ny < height
                    and (nx, ny) not in logo_set
                    and is_open(grid, x, y, d) and (nx, ny) not in seen):
                seen.add((nx, ny))
                queue.append((nx, ny))
    return seen


def print_maze(grid, width, height, logo):
    """Dibuja el laberinto en ASCII destacando el logo de 42."""
    logo_set = set(logo)
    out = ["+" + "---+" * width]
    for y in range(height):
        row, below = "|", "+"
        for x in range(width):
            if (x, y) in logo_set:
                row += " 42" + ("|" if grid[y][x] & BIT["E"] else " ")
                below += "---+" if grid[y][x] & BIT["S"] else "   +"
            else:
                row += "   " + ("|" if grid[y][x] & BIT["E"] else " ")
                below += ("---" if grid[y][x] & BIT["S"] else "   ") + "+"
        out += [row, below]
    print("\n".join(out))


def test_dimensions():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            logo = get_logo(h, w)
            grid = gen(w, h, (0, 0), 42, True, logo)
            assert len(grid) == h, f"{name} {w}x{h}: alto incorrecto"
            assert all(len(r) == w for r in grid), \
                f"{name} {w}x{h}: ancho incorrecto"


def test_cell_values_valid():
    for name, gen in GENERATORS.items():
        logo = get_logo(10, 10)
        grid = gen(10, 10, (0, 0), 1, True, logo)
        assert all(0 <= c <= 15 for row in grid for c in row), \
            f"{name}: valores fuera de 0-15"


def test_borders_closed():
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            logo = get_logo(h, w)
            grid = gen(w, h, (0, 0), 7, True, logo)
            for x in range(w):
                assert grid[0][x] & BIT["N"], f"{name} {w}x{h}: borde N abierto x={x}"
                assert grid[h - 1][x] & BIT["S"], f"{name} {w}x{h}: borde S abierto x={x}"
            for y in range(h):
                assert grid[y][0] & BIT["W"], f"{name} {w}x{h}: borde W abierto y={y}"
                assert grid[y][w - 1] & BIT["E"], f"{name} {w}x{h}: borde E abierto y={y}"


def test_logo_cells_closed():
    """Verifica que las celdas del logo mantienen sus 4 muros cerrados (valor 15)."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            logo = get_logo(h, w)
            grid = gen(w, h, (0, 0), 42, True, logo)
            for x, y in logo:
                assert grid[y][x] == 15, \
                    f"{name} {w}x{h}: la celda del logo en ({x},{y}) no está completamente cerrada (valor {grid[y][x]})"


def test_walls_symmetric():
    """Si A tiene abierto el muro hacia B, B debe tenerlo abierto hacia A."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            logo = get_logo(h, w)
            for perfect_flag in [True, False]:
                grid = gen(w, h, (0, 0), 3, perfect_flag, logo)
                for y in range(h):
                    for x in range(w):
                        for d, (dx, dy) in DELTA.items():
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                assert is_open(grid, x, y, d) == \
                                    is_open(grid, nx, ny, OPPOSITE[d]), \
                                    f"{name} {w}x{h} (perfect={perfect_flag}): muro incoherente ({x},{y}) {d}"


def test_all_cells_reachable():
    """Sin zonas aisladas: se llega a todas las celdas (excepto el logo)."""
    for name, gen in GENERATORS.items():
        for w, h in SIZES:
            logo = get_logo(h, w)
            logo_set = set(logo)
            for seed in range(3):
                for perfect_flag in [True, False]:
                    grid = gen(w, h, (0, 0), seed, perfect_flag, logo)
                    reached = reachable(grid, w, h, (0, 0), logo)
                    expected_count = (w * h) - len(logo_set)
                    assert len(reached) == expected_count, \
                        f"{name} {w}x{h} seed={seed} perfect={perfect_flag}: hay celdas aisladas fuera del logo"


def test_reproducible_same_seed():
    for name, gen in GENERATORS.items():
        logo = get_logo(15, 15)
        assert gen(15, 15, (0, 0), 1234, True, logo) == gen(15, 15, (0, 0), 1234, True, logo), \
            f"{name}: misma seed, distinto laberinto (perfect=True)"
        assert gen(15, 15, (0, 0), 1234, False, logo) == gen(15, 15, (0, 0), 1234, False, logo), \
            f"{name}: misma seed, distinto laberinto (perfect=False)"


def test_different_seeds_differ():
    for name, gen in GENERATORS.items():
        logo = get_logo(15, 15)
        assert gen(15, 15, (0, 0), 1, True, logo) != gen(15, 15, (0, 0), 2, True, logo), \
            f"{name}: seeds distintas, mismo laberinto (perfect=True)"


def test_seed_none_works():
    for name, gen in GENERATORS.items():
        logo = get_logo(8, 8)
        grid = gen(8, 8, (0, 0), None, True, logo)
        logo_set = set(logo)
        assert len(reachable(grid, 8, 8, (0, 0), logo)) == 64 - len(logo_set), f"{name}: seed=None falla"


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
    print("=== MUESTRA VISUAL DEL LABERINTO CON EL LOGO DE '42' ===")
    for gname, gen in GENERATORS.items():
        try:
            w, h = 9, 7
            logo_coords = get_logo(h, w)
            print(f"\nGenerador: {gname} ({w}x{h}, seed {seed}, PERFECT=False):")
            grid_result = gen(w, h, (0, 0), None, False, logo_coords)
            print_maze(grid_result, w, h, logo_coords)
        except Exception as e:  # noqa: BLE001
            print(f"  no se pudo generar: {type(e).__name__}: {e}")
    sys.exit(1 if failed else 0)