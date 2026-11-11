# Arquitectura de A-Maze-Ing

## 1. Vista general

El proyecto se divide en dos capas principales:

```text
a_maze_ing.py
    │
    ▼
app/                      aplicación de terminal
    ├── config.py         lectura y validación
    ├── controller.py     orquestación
    ├── output.py         formato de salida
    ├── menu.py           interacción
    ├── themes.py         paletas ANSI
    └── renderers/
        └── console.py    dibujo ASCII/ANSI

mazegen/                  biblioteca reutilizable
    ├── model.py          Maze, Cell, Direction, MazeError
    ├── pattern42.py      colocación del glifo 42
    ├── algorithms.py     recursive backtracker, hunt-and-kill
    ├── solver.py         BFS
    └── generator.py      fachada MazeGenerator
```

`mazegen` no importa nada de `app`. La aplicación depende de `mazegen`,
nunca al revés.

## 2. Modelo de datos

### `Cell`

Contiene una máscara de cuatro bits (`walls`) y un marcador `visited`.
Un bit a 1 significa pared cerrada. La codificación coincide con la
salida hexadecimal: `N=1`, `E=2`, `S=4`, `W=8`.

### `Maze`

Mantiene `grid[y][x]`, las coordenadas de entrada y salida y el conjunto
de celdas del patrón `42`. Sus invariantes son:

- las paredes compartidas se abren o cierran en ambos lados;
- las celdas del patrón están totalmente cerradas y no se pueden abrir;
- las paredes del borde exterior no se pueden abrir;
- las celdas fuera del patrón forman una única región conexa.

Métodos relevantes:

- `get_cell`, `get_neighbor`, `has_wall`;
- `open_wall`, `close_wall`;
- `open_neighbors`, `region`;
- `is_fully_connected`, `count_loops`, `has_open_3x3`;
- `to_hex_rows`.

## 3. Generación

### Fachada `MazeGenerator`

Valida argumentos, elige una semilla si no se proporciona y llama a
`place_pattern42`. Después construye un `Maze`, ejecuta el algoritmo de
expansión y, si el modo no es perfecto, aplica `braid`.

La fachada expone:

- `generate() -> Maze`;
- `solve() -> str`;
- `seed`;
- `pattern42_present`;
- `last_warning`.

### Algoritmos

- `recursive_backtracker`: pila explícita, elige vecinos no visitados al
  azar y retrocede.
- `hunt_and_kill`: camino aleatorio + búsqueda de una celda no visitada
  con vecino visitado.

Ambos producen un árbol de expansión sobre las celdas libres.

### Braiding

En modo jugable:

1. se eliminan dead-ends reales abriendo una pared segura;
2. se añaden ciclos hasta alcanzar al menos dos rutas independientes;
3. cada apertura se rechaza si genera un bloque abierto de `3x3`.

`count_loops()` calcula los ciclos independientes como
`pasillos - celdas + componentes`.

### Patrón 42

El glifo es una matriz de 5 filas y 7 columnas. Se busca una posición
centrada que:

- no toque entrada, salida, esquinas ni centro;
- deje el resto del tablero conectado.

Si no hay posición válida o el tablero mide menos de `9x7`, se omite y
se devuelve un aviso.

## 4. Resolución

`solver.shortest_path` recorre el grafo con BFS desde la entrada. Los
vecinos se examinan en orden `N`, `E`, `S`, `W`. Se guarda el padre de
cada celda y se reconstruye el camino. Las celdas del patrón `42` nunca
se atraviesan.

## 5. Aplicación

### Configuración

`app.config.MazeConfig.from_file` lee el fichero completo, elimina
comentarios, normaliza claves a mayúsculas, detecta duplicados y valida
tipos, coordenadas, límites y valores cerrados. Lanza `ConfigError`.

### Controlador

`MazeController` mantiene:

- configuración;
- algoritmo y tema actuales;
- visibilidad del camino;
- número de regeneraciones;
- última generación.

`run()` genera, escribe, muestra y decide si abrir el menú. La decisión
depende de `stdin.isatty()` y de `AMAZEING_NO_MENU`.

### Menú

`Menu.prompt` valida números del 1 al 5 y devuelve `None` si la entrada
se cierra. El controlador ejecuta la acción y redibuja.

### Renderizador

`ConsoleRenderer` dibuja:

- línea superior de muros;
- una línea de celdas y otra de muros por fila;
- `S` para entrada, `E` para salida, `*` para camino y `###` para el
  patrón;
- colores ANSI opcionales.

El render es independiente de `curses` y funciona en cualquier terminal
con texto ASCII.

### Salida

`app.output.build_output` construye el texto exacto. `write_maze` crea
el directorio padre y escribe con `newline="\n"`.

## 6. Flujo de una ejecución

```text
argv
  │
  ▼
a_maze_ing.main
  │
  ├── MazeConfig.from_file
  │
  ▼
MazeController.run
  │
  ├── MazeGenerator.generate
  │     ├── place_pattern42
  │     ├── carve_spanning_tree
  │     └── braid (si PERFECT=False)
  │
  ├── MazeGenerator.solve (BFS)
  ├── write_maze
  ├── ConsoleRenderer.render
  └── Menu (si hay TTY)
```

## 7. Empaquetado

`pyproject.toml` define el paquete `mazegen` con `setuptools`, incluye
`mazegen/py.typed` y declara Python 3.10+. `make build` genera wheel y
sdist; `make install` instala el paquete en modo editable junto con las
herramientas de desarrollo.

## 8. Compatibilidad

Los directorios `core/`, `config/`, `renderer/`, `themes/` y `utils/`
conservan envoltorios mínimos para importaciones antiguas, pero toda la
lógica nueva vive en `mazegen` y `app`.
