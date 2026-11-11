# Matriz de evaluación

Esta matriz relaciona los puntos de `docs/project_evaluation.md` con la
implementación y las pruebas del repositorio.

## 1. Contenido obligatorio del repositorio

| Elemento | Estado | Evidencia |
| --- | --- | --- |
| `README.md` | Cumplido | README con primera línea obligatoria, Description, Instructions, Resources, configuración, algoritmos, módulo, equipo e IA |
| `LICENSE.md` | Cumplido | Licencia MIT con los dos logins |
| `a_maze_ing.py` | Cumplido | Entry point con 0/1 argumentos y errores controlados |
| Artefacto `mazegen-*.whl` / `.tar.gz` | Cumplido | `make build` o `python -m pip wheel . --no-deps -w .` |
| Fichero de configuración | Cumplido | `config/config.txt` |
| Elementos para reconstruir | Cumplido | `pyproject.toml`, `mazegen/`, `py.typed` |
| `flake8` | Cumplido | `python -m flake8 .` |
| `mypy` | Cumplido | `python -m mypy . --warn-return-any ...` |

## 2. README

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Primera línea exacta | Cumplido | `*This project has been created as part of the 42 curriculum by jgilaber, p-vivas.*` |
| Description | Cumplido | Sección `## Description` |
| Instructions | Cumplido | Sección `## Instructions` |
| Resources | Cumplido | Sección `## Resources` |
| Uso de IA | Cumplido | Subsección `### Uso de IA` |
| Configuración completa | Cumplido | Tablas de claves obligatorias y opcionales |
| Algoritmo y motivo | Cumplido | Sección `## Maze Generation Algorithm` |
| Módulo reutilizable | Cumplido | Sección `## Reusable Maze Generator` |
| Roles y planificación | Cumplido | Sección `## Team and Project Management` |
| Herramientas | Cumplido | Subsección `### Herramientas utilizadas` |

## 3. Uso estándar

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Ejecutar con configuración por defecto | Cumplido | `python3 a_maze_ing.py` |
| Generar y mostrar laberinto | Cumplido | `MazeController.run` + `ConsoleRenderer` |
| Regenerar laberinto | Cumplido | Opción 1 del menú |
| Mostrar camino | Cumplido | Opción 2 |
| Ocultar camino | Cumplido | Opción 2 (toggle) |
| Cambiar color de paredes | Cumplido | Opción 3, seis temas |
| Interacción sin crash | Cumplido | `Menu.prompt` valida y el controlador captura errores |
| Modo no interactivo | Cumplido | `AMAZEING_NO_MENU=1` y detección de TTY |

## 4. Configuración

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Falta una clave obligatoria | Cumplido | `ConfigError` + test |
| Línea sin `=` | Cumplido | `ConfigError` + test |
| Números inválidos | Cumplido | `_parse_positive_int` + tests |
| `PERFECT` inválido | Cumplido | `_parse_bool` + test |
| `ENTRY`/`EXIT` inválidos | Cumplido | `_parse_coordinates` + tests |
| Sin terminación inesperada | Cumplido | `main` captura errores y devuelve 1 |

## 5. Fichero de salida

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| `HEIGHT` líneas | Cumplido | `app/output.py` + `tests/test_output.py` |
| `WIDTH` caracteres por línea | Cumplido | `to_hex_rows` + test |
| Línea vacía | Cumplido | `build_output` + test |
| Entrada y salida | Cumplido | `build_output` + test |
| Camino `N/E/S/W` | Cumplido | BFS + test |
| Newlines correctos | Cumplido | `newline="\n"` + test |
| Analizador oficial | Cumplido | `tests/test_analyzer.py` |

## 6. Módulo generador

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Generación aleatoria | Cumplido | `random.Random` con semilla |
| Entrada fuera del laberinto | Cumplido | `MazeGenerator._validate_arguments` |
| Salida fuera del laberinto | Cumplido | `MazeGenerator._validate_arguments` |
| Dimensiones negativas | Cumplido | Validación + tests |
| Conectividad | Cumplido | `is_fully_connected` + tests |
| Paredes exteriores | Cumplido | `open_wall` no abre bordes + test |
| Sin `3x3` | Cumplido | `has_open_3x3` + tests |
| Patrón `42` | Cumplido | `pattern42.py` + test de forma |
| Aviso si no cabe | Cumplido | `last_warning` + test |

## 7. `PERFECT=True`

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Laberinto perfecto | Cumplido | Árbol de expansión |
| Un solo camino | Cumplido | `count_loops() == 0` |
| Sin loops | Cumplido | Validación del generador |

## 8. `PERFECT=False`

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Tablero tipo Pac-Man | Cumplido | Braiding |
| Todos los corredores alcanzables | Cumplido | `is_fully_connected` |
| Esquinas abiertas | Cumplido | `pattern42` las protege + test |
| Centro abierto | Cumplido | `pattern42` lo protege + test |
| Al menos dos rutas | Cumplido | `count_loops() >= 2` + test |
| Dead-ends tolerados | Cumplido | 0 reales en 20x15 + test |
| Bonus sin dead-ends | Cumplido | `real_dead_end_cells() == []` |

## 9. Reproducibilidad

| Prueba | Estado | Evidencia |
| --- | --- | --- |
| Misma semilla, mismo laberinto | Cumplido | `test_seed_is_reproducible` |
| Semillas distintas, laberintos distintos | Cumplido | `test_different_seeds_produce_different_mazes` |

## 10. Comandos de verificación

```bash
python -m flake8 .
python -m mypy . --warn-return-any --warn-unused-ignores \
  --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
python -m pytest tests -q
AMAZEING_NO_MENU=1 python3 a_maze_ing.py
python3 maze_analyzer.py output/maze.txt
python -m pip wheel . --no-deps -w .
```

## 11. Limitaciones conocidas

- No se implementa MiniLibX; el subject permite terminal y la hoja de
  evaluación acepta el render ASCII.
- En tamaños muy pequeños puede no ser posible dibujar el `42` ni
  alcanzar dos ciclos; el programa avisa y sigue funcionando.
- El analizador oficial no comprueba la forma del `42`, el camino ni
  `3x3`; esas invariantes se cubren con pruebas propias.
