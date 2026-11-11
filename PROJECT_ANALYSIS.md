# Análisis del proyecto A-Maze-Ing

## 1. Objetivo

Construir un generador de laberintos reproducible, con dos modos de
juego y una salida hexadecimal verificable, manteniendo separada la
biblioteca reutilizable (`mazegen`) de la aplicación de terminal
(`app`).

## 2. Requisitos funcionales

| Requisito | Implementación |
| --- | --- |
| Generación aleatoria con semilla | `MazeGenerator(seed=...)` y `random.Random` |
| Paredes coherentes | `Maze.open_wall` y `close_wall` modifican ambos lados |
| Conectividad completa salvo el patrón `42` | `Maze.is_fully_connected()` y validación del generador |
| Sin zonas abiertas de `3x3` | `Maze.has_open_3x3()` y rechazo al abrir paredes |
| Patrón `42` visible | `mazegen/pattern42.py` + render `###` |
| Aviso si el patrón no cabe | `MazeGenerator.last_warning` y `stderr` |
| `PERFECT=True` sin ciclos | Árbol de expansión y `count_loops() == 0` |
| `PERFECT=False` tipo Pac-Man | Braiding, esquinas/centro abiertos, ≥2 ciclos |
| Sin dead-ends reales | `braid()` elimina callejones cuando es posible |
| Salida hexadecimal | `app/output.py` y `Maze.to_hex_rows()` |
| Camino más corto | BFS en `mazegen/solver.py` |
| Configuración `KEY=VALUE` | `app/config.py`, claves case-insensitive |
| Menú interactivo | `app/menu.py` y `app/controller.py` |
| Render ASCII/ANSI | `app/renderers/console.py` |
| Paquete reutilizable | `pyproject.toml` y `mazegen/` |
| Analizador oficial | copia literal `maze_analyzer.py` |

## 3. Decisiones de diseño

### 3.1 Paquete en lugar de un módulo único

El subject exige reutilización. Se creó `mazegen/` con API pública
mínima (`MazeGenerator`, `Maze`, `Cell`, `Direction`, `MazeError`) y
sin dependencias de la aplicación. Esto permite instalar el paquete con
`pip` y usarlo desde otro proyecto.

### 3.2 Renderizador de terminal obligatorio

El renderizador de terminal es portable y no requiere `curses` ni
MiniLibX. Los colores ANSI se desactivan con `NO_COLOR` o cuando la
salida no es un TTY. MiniLibX es específico de Linux y no se usa por
defecto.

### 3.3 Generación en dos fases

1. Se coloca el patrón `42` (celdas cerradas).
2. Se construye un árbol de expansión sobre las celdas libres.
3. Si `PERFECT=False`, se aplica braiding para crear ciclos y eliminar
   dead-ends, rechazando cualquier apertura que cree un `3x3`.

Esta separación hace que el modo perfecto sea fácil de razonar y que el
modo jugable reutilice el mismo esqueleto.

### 3.4 BFS para la solución

Todas las aristas tienen coste 1. BFS es suficiente, determinista y
lineal; no se necesita A* ni Dijkstra.

### 3.5 Configuración estricta

Las claves desconocidas y duplicadas producen error para evitar erratas
silenciosas. Las claves opcionales permiten semilla, algoritmo, tema y
renderizador. Los errores se muestran sin traceback y con código de
salida 1.

## 4. Formato de salida

1. `HEIGHT` filas hexadecimales, una celda por dígito.
2. Línea vacía.
3. `ENTRY` en formato `x,y`.
4. `EXIT` en formato `x,y`.
5. Camino más corto con `N/E/S/W`.
6. Todas las líneas terminan en `\n`.

Bits: `N=1`, `E=2`, `S=4`, `W=8`; un bit a 1 significa muro cerrado.

## 5. Estrategia de pruebas

- `tests/test_config.py`: configuración válida, defaults, BOM/CRLF,
  errores de sintaxis y semántica.
- `tests/test_maze.py`: modelo de celdas, coherencia, límites, ciclos,
  `3x3`, patrón protegido.
- `tests/test_generator.py`: ambos algoritmos, ambos modos, semilla,
  estructura, patrón `42`, tamaños pequeños y parámetros inválidos.
- `tests/test_hunt_and_kill.py`: pruebas específicas del segundo
  algoritmo.
- `tests/test_output.py`: formato exacto, newlines, ruta y camino.
- `tests/test_app.py`: render, controlador, menú, configuración por
  defecto, un argumento y errores.
- `tests/test_analyzer.py`: integración con `maze_analyzer.py`,
  veredictos y fichero malformado.

## 6. Calidad y riesgos

Controles ejecutados:

```bash
python -m flake8 .
python -m mypy . --warn-return-any --warn-unused-ignores \
  --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
python -m pytest tests -q
python maze_analyzer.py output/maze.txt
```

Riesgos y mitigaciones:

- **MiniLibX no implementado**: el subject permite terminal; el paquete
  no depende de MLX y `renderer/MiniLibX.py` solo informa de su
  disponibilidad.
- **Tamaños muy pequeños**: el patrón `42` se omite con aviso y el modo
  jugable puede no alcanzar dos ciclos; se emite un aviso.
- **Analizador oficial limitado**: no comprueba la forma del `42`, el
  camino ni `3x3`; por eso hay pruebas propias para esas invariantes.
- **Codificación en Windows**: el render usa solo ASCII para evitar
  problemas con `cp1252`.

## 7. Conclusión

La solución cumple los requisitos obligatorios, separa biblioteca y
aplicación, documenta el formato y cuenta con pruebas automáticas y
análisis estático. Las limitaciones conocidas están acotadas y
documentadas.
