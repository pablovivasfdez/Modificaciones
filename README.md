1. Makefile -> LISTO
2. pyproject.toml -> Se supone que esta listo. Realizar una ultima revision al final del proyecto.
3. requirements.txt -> Revisar si se han incluido todas aquellas dependencias que no vienen con python por defecto al final del proyecto.
4. gitignore -> LISTO. Realizar una ultima revision al final del proyecto.
5. config parser -> LISTO
6. representación Cell/Maze -> LISTO
7. MazeGenerator(BFS)
8. PERFECT=True
9. solución A*
10. output hexadecimal
11. validación(SUPONGO QUE DEL OUPUT HEXADECIMAL)
12. PERFECT=False
13. "42" -> ERROR. ESTO SE HACE LO PRIMERO EN EL BFS
14. renderer ASCII
15. tests
16. packaging mazegen
17. README
18. revisión final con flake8 + mypy

*This project has been created as part of the 42 curriculum by jgilaber y p-vivasf.*

# A-Maze-ing

## Description

La aplicación lee un fichero de configuración, genera un laberinto,
calcula el camino más corto entre la entrada y la salida, guarda el
resultado en un fichero de texto y lo muestra en el terminal con un menú
interactivo.

El proyecto permite practicar:

- programación en Python;
- diseño de algoritmos y estructuras de datos;
- generación de laberintos y resolución de caminos mínimos;
- lectura y validación de ficheros de configuración;
- gestión de errores;
- renderizado ASCII/ANSI;
- pruebas automáticas, `flake8` y `mypy`;
- empaquetado de una biblioteca reutilizable.

Características principales:

- Modo perfecto (`PERFECT=True`): árbol de expansión, sin ciclos.
- Modo jugable (`PERFECT=False`): tablero tipo Pac-Man, conectado, con
  las esquinas y el centro abiertos y varias rutas independientes.
- Patrón `42` dibujado con celdas totalmente cerradas cuando el tamaño
  lo permite.
- Dos algoritmos: `recursive_backtracker` y `hunt_and_kill`.
- Renderizado de terminal con colores ANSI y seis temas.
- Menú para regenerar, mostrar u ocultar el camino, cambiar el tema y
  cambiar el algoritmo.
- Salida hexadecimal compatible con `maze_analyzer.py`.

## Instructions

### Requisitos

- Python 3.10 o superior.
- `make` para usar los objetivos del Makefile.
- No se necesitan dependencias externas para ejecutar la aplicación; las
  herramientas de desarrollo están en `dependencies/requirements.txt`.

### Instalación

Desde la raíz del repositorio:

```bash
make install
```

El objetivo crea un entorno virtual `.venv`, instala las herramientas de
desarrollo y el paquete `mazegen` en modo editable.

También se puede hacer manualmente:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r dependencies/requirements.txt
python3 -m pip install -e .
```

### Ejecución

Con el fichero de configuración por defecto:

```bash
python3 a_maze_ing.py
```

Con un fichero concreto:

```bash
python3 a_maze_ing.py config/config.txt
```

La aplicación escribe el primer laberinto y cada regeneración en el
fichero indicado por `OUTPUT_FILE`. Si la entrada estándar no es un TTY
o si se define `AMAZEING_NO_MENU=1`, se imprime el laberinto y el
programa termina sin abrir el menú.

### Makefile

```bash
make install      # crea el entorno e instala dependencias
make run          # ejecuta la aplicación con config/config.txt
make debug        # ejecuta la aplicación con pdb
make lint         # flake8 + mypy
make lint-strict  # flake8 + mypy --strict
make test         # pytest
make build        # construye wheel y sdist en la raíz
make clean        # limpia cachés y artefactos de construcción
make fclean       # limpia también el entorno virtual
```

### Pruebas

```bash
make test
```

Las pruebas cubren configuración, modelo del laberinto, generadores,
patrón `42`, formatos de salida, renderizado, menú, errores y el
analizador oficial.

## Configuration File

El fichero de configuración usa una pareja `KEY=VALUE` por línea. Las
claves no distinguen mayúsculas de minúsculas, los espacios alrededor de
`=` se ignoran y las líneas que empiezan por `#` son comentarios.
También se permiten comentarios al final de una línea.

### Claves obligatorias

| Clave | Descripción | Ejemplo |
| --- | --- | --- |
| `WIDTH` | Ancho del laberinto en celdas | `WIDTH=20` |
| `HEIGHT` | Alto del laberinto en celdas | `HEIGHT=15` |
| `ENTRY` | Coordenadas de entrada `x,y` | `ENTRY=0,0` |
| `EXIT` | Coordenadas de salida `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Ruta del fichero de salida | `OUTPUT_FILE=output/maze.txt` |
| `PERFECT` | Activa el modo perfecto | `PERFECT=True` |

### Claves opcionales

| Clave | Descripción | Valores | Defecto |
| --- | --- | --- | --- |
| `SEED` | Semilla reproducible | entero | aleatoria |
| `ALGORITHM` | Algoritmo de generación | `recursive_backtracker`, `hunt_and_kill` | `recursive_backtracker` |
| `THEME` | Tema de colores ANSI | `midnight`, `obsidian`, `arctic`, `solar`, `ocean`, `synthwave` | `midnight` |
| `RENDERER` | Renderizador | `terminal` | `terminal` |

### Ejemplo

```text
# Configuración por defecto
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=output/maze.txt
PERFECT=False
SEED=42
ALGORITHM=recursive_backtracker
THEME=midnight
RENDERER=terminal
```

Si una clave obligatoria falta, una línea no tiene `=`, una coordenada
está fuera del tablero, `ENTRY` y `EXIT` coinciden o un valor no es
válido, el programa muestra un error claro y termina con código 1 sin
traceback.

## Output Format

El fichero de salida contiene, en este orden:

1. `HEIGHT` líneas con exactamente `WIDTH` dígitos hexadecimales.
2. Una línea vacía.
3. La entrada en formato `x,y`.
4. La salida en formato `x,y`.
5. El camino más corto usando solo `N`, `E`, `S` y `W`.

Cada celda usa un dígito hexadecimal cuyos bits indican muros cerrados:

| Bit | Valor | Dirección |
| --- | --- | --- |
| 0 | 1 | Norte (`N`) |
| 1 | 2 | Este (`E`) |
| 2 | 4 | Sur (`S`) |
| 3 | 8 | Oeste (`W`) |

Ejemplo de estructura:

```text
<HEIGHT líneas hexadecimales>

0,0
19,14
EESENEEESENEEEEESEESSENEEENNESSSSWWWSWNWSSSENESSSWSESSESSENNNESSS
```

Todas las líneas terminan con `\n`, incluida la última.

## Maze Generation Algorithm

### Algoritmo principal

El algoritmo por defecto es **recursive backtracker** iterativo. Se
parte de la entrada, se marca la celda como visitada y se abre una pared
hacia un vecino no visitado elegido al azar. Cuando no quedan vecinos,
se retrocede en la pila. El resultado es un árbol de expansión: todas
las celdas no ocupadas por el patrón `42` quedan conectadas y no se crea
ningún ciclo.

También se puede elegir **hunt-and-kill**. Este algoritmo explora un
camino aleatorio y, cuando se queda sin vecinos, busca la primera celda
no visitada que tenga un vecino visitado, conecta ambas y continúa. Es
una alternativa clásica que produce laberintos perfectos con una
estructura diferente.

### Por qué se eligió

El recursive backtracker es sencillo de implementar sin recursión real,
genera pasillos largos y es fácil de reproducir con una semilla. Al
construir un árbol de expansión, cumple directamente la condición de
laberinto perfecto. Hunt-and-kill se mantiene como segundo algoritmo
para demostrar que el generador es intercambiable y para el bonus de
algoritmos múltiples.

### Modo jugable y patrón 42

Cuando `PERFECT=False`, después de construir el árbol se aplica un
proceso de *braiding*: se eliminan callejones sin salida abriendo paredes
y se añaden ciclos hasta conseguir al menos dos rutas independientes.
Cada apertura se rechaza si produce una zona abierta de `3x3`.

El patrón `42` se coloca antes de generar los pasillos. Está formado por
celdas totalmente cerradas, intenta quedar centrado y nunca ocupa la
entrada, la salida, las esquinas ni el centro. Si el laberinto es menor
de `9x7` o no existe una colocación válida, el patrón se omite y se
muestra un aviso por el terminal.

## Maze Solving Algorithm

### Algorithm overview

### Why this algorithm?

## Maze Representation

Cada celda es un objeto `Cell` con una máscara de cuatro bits. Un bit a
1 significa que la pared está cerrada. Abrir una pared modifica
simultáneamente las dos celdas vecinas, de modo que nunca hay paredes
incoherentes.

El laberinto se representa con `Maze`, que ofrece:

- `width` y `height`;
- `entry` y `exit`;
- `get_cell(x, y)`;
- `has_wall(x, y, direction)`;
- `open_wall(x, y, direction)` y `close_wall(x, y, direction)`;
- `open_neighbors(x, y)` y `region(start)`;
- `is_fully_connected()`, `count_loops()` y `has_open_3x3()`;
- `to_hex_rows()` para exportar la cuadrícula;
- `pattern42_cells` para consultar las celdas cerradas del patrón.

## Visual Representation

La representación obligatoria es de terminal, sin `curses`, y funciona en
Linux, macOS y Windows. Cada celda ocupa tres columnas y los muros se
dibujan con `+`, `-` y `|`. La entrada se muestra como `S`, la salida
como `E`, el camino como `*` y las celdas del patrón `42` como bloques
`###` coloreados.

Los colores ANSI se desactivan automáticamente si `NO_COLOR` está
definida o si la salida no es un TTY. El menú permite:

1. regenerar el laberinto;
2. mostrar u ocultar el camino más corto;
3. cambiar el tema de colores;
4. cambiar el algoritmo y regenerar;
5. salir.

MiniLibX no es obligatorio para este proyecto y no se usa en la
ejecución por defecto. `renderer/MiniLibX.py` solo comprueba si las
bindings están disponibles.

## Reusable Maze Generator

### Instalación del paquete

El paquete se puede construir e instalar de forma independiente:

```bash
python -m build
python -m pip install mazegen-1.0.0-py3-none-any.whl
```

`make build` genera los artefactos `mazegen-1.0.0.tar.gz` y
`mazegen-1.0.0-py3-none-any.whl` en la raíz del repositorio.

### Uso básico

```python
from mazegen import MazeGenerator

generator = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42,
    algorithm="recursive_backtracker",
)
maze = generator.generate()
solution = generator.solve()

print(solution)
print(generator.seed)
```

### Parámetros personalizados

- `width` y `height`: tamaño en celdas.
- `entry` y `exit`: tuplas `(x, y)`.
- `perfect`: `True` para árbol sin ciclos; `False` para tablero jugable.
- `seed`: entero para reproducibilidad; si se omite se elige una.
- `algorithm`: `"recursive_backtracker"` o `"hunt_and_kill"`.
- `pattern42`: `True` por defecto; se puede desactivar.

### Acceso a la estructura

```python
from mazegen import Direction

cell = maze.get_cell(0, 0)
print(cell.walls)
print(maze.has_wall(0, 0, Direction.NORTH))
print(maze.count_loops())
print(maze.real_dead_end_cells())
print(maze.pattern42_cells)
```

### Acceso a la solución

```python
path = generator.solve()
```

El resultado usa únicamente `N`, `E`, `S` y `W`. Si no existe camino,
se lanza `MazeError`.

### Avisos

`generator.last_warning` contiene un texto en español cuando el patrón
`42` no cabe o cuando el tablero es demasiado pequeño para cumplir
alguna condición del modo jugable. La aplicación muestra ese aviso por
`stderr`.


## Resources

- Documentación oficial de Python: `random`, `dataclasses`, `pathlib`,
  `typing`, `unittest`/`pytest`.
- Subject del proyecto A-Maze-Ing.
- Documentación de `flake8`: <https://flake8.pycqa.org/>
- Documentación de `mypy`: <https://mypy.readthedocs.io/>
- Documentación de `pytest`: <https://docs.pytest.org/>

### Uso de IA

Se utilizó un asistente de IA como apoyo para:

- revisar la arquitectura y proponer una separación entre `mazegen` y la
  aplicación;
- generar borradores de código y de pruebas;
- revisar mensajes de error, formato de salida y casos límite;
- redactar parte de la documentación.

Todo el código generado se revisó, se ejecutó y se adaptó manualmente.
Las decisiones finales de diseño, la validación con `flake8`, `mypy`,
`pytest` y `maze_analyzer.py`, y la comprobación del comportamiento en
terminal fueron responsabilidad de los autores.

## Team and Project Management

### Roles

- **jgilaber**: diseño del modelo de celdas y laberinto, configuración, menú interactivo, readme, makefile, gitignore, license.
- **p-vivas**: aplicación de terminal, resolución y empaquetado del módulo reutilizable, generación,
  patrón `42`, renderizado, pruebas de integración y documentación.

Ambos miembros revisaron el código, probaron los casos de error y
validaron la salida con el analizador.

### Planificación y evolución

La planificación inicial dividía el trabajo en modelo, generadores,
solver, renderizado, configuración, salida, pruebas y empaquetado. La
primera versión del repositorio contenía un esqueleto con módulos
antiguos y pruebas incompletas. Durante el desarrollo se decidió:

- sustituir el modelo antiguo por el paquete `mazegen`;
- mantener un renderizador de terminal portable en lugar de depender de
  MiniLibX;
- concentrar la validación de configuración en `app/config.py`;
- usar BFS en lugar de A* para el camino más corto;
- añadir un modo no interactivo para pruebas automatizadas.

### Qué funcionó bien

- La separación entre biblioteca y aplicación facilitó las pruebas.
- La semilla fija permitió reproducir fallos y comparar salidas.
- El analizador oficial se usó como prueba de integración.
- El *braiding* con comprobación de `3x3` produjo tableros jugables sin
  callejones sin salida en los tamaños probados.

### Qué se podría mejorar

- Añadir un renderizador MiniLibX real para entornos Linux con MLX.
- Incorporar más algoritmos de generación y benchmarks.
- Añadir pruebas visuales automatizadas del dibujo ASCII.
- Internacionalizar los mensajes de la aplicación.

### Herramientas utilizadas

- Python 3.10+.
- `pytest`, `flake8` y `mypy`.
- `build` y `setuptools` para el paquete.
- `maze_analyzer.py` proporcionado por 42.
- Terminal ANSI y Git.

## Advanced Features / Bonuses

- Dos algoritmos de generación intercambiables.
- Tablero jugable sin callejones sin salida reales en los tamaños
  habituales.
- Seis temas de color.
- Patrón `42` centrado y protegido.
- Menú interactivo con regeneración y cambio de algoritmo.
- Analizador propio integrado en las pruebas(REVISAR).

## Disclaimer

Este repositorio contiene una solución personal al proyecto A-Maze-Ing
de 42. El subject y los materiales proporcionados por 42 no son trabajo
original de los autores.

## License

MIT License. Consulta [LICENSE.md](LICENSE.md).


## Project Architecture

La arquitectura se divide en varias capas: configuración, generación,
representación del laberinto y salida/consumo del laberinto.

```text
config.txt
    │
    ▼
┌──────────────────┐
│ MazeConfigParser │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│    MazeConfig    │
└────────┬─────────┘
         │
         ▼
┌─────────────────┐
│  MazeGenerator  │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
 PERFECT   PLAYABLE
 Generator  Generator
    │         │
    └────┬────┘
         │
         ▼
┌─────────────────────────┐
│          Maze           │
│                         │
│  Cell  Cell  Cell       │
│  Cell  Cell  Cell       │
│  Cell  Cell  Cell       │
└───────────┬─────────────┘
            │
       ┌────┼────┐
       │    │    │
       ▼    ▼    ▼
    Solver Renderer Writer
       │    │    │
       ▼    ▼    ▼
   N E E S  │  maze.txt
            │
      Terminal/MiniLibX
```