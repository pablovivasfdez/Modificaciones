"""Carga y validación del fichero de configuración."""  

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Final, override

from .themes import THEME_NAMES

ALGORITHMS: Final[tuple[str, ...]] = (
    "recursive_backtracker",
    "hunt_and_kill",
)
RENDERERS: Final[tuple[str, ...]] = ("terminal",)

DEFAULT_ALGORITHM: Final[str] = "recursive_backtracker"
DEFAULT_THEME: Final[str] = "midnight"
DEFAULT_RENDERER: Final[str] = "terminal"

MANDATORY_KEYS: Final[tuple[str, ...]] = (
    "WIDTH",
    "HEIGHT",
    "ENTRY",
    "EXIT",
    "OUTPUT_FILE",
    "PERFECT",
)
OPTIONAL_KEYS: Final[tuple[str, ...]] = (
    "SEED",
    "ALGORITHM",
    "THEME",
    "RENDERER",
)
KNOWN_KEYS: Final[frozenset[str]] = frozenset(
    MANDATORY_KEYS + OPTIONAL_KEYS
)


class ConfigError(ValueError):
    """Config error con un mensaje comprensible."""
    @override
    def __str__(self) -> str:
        if not self.args:
            return f"Config error desconocido: {self.__class__.__name__}"
        return f"Config error {self.__class__.__name__}: {self.args[0]}"


@dataclass
class MazeConfig:
    """Configuración validada de la aplicación A-Maze-ing.

    Attributes:
        width: Ancho del laberinto en celdas.
        height: Alto del laberinto en celdas.
        entry: Coordenadas ``(x, y)`` de la entrada.
        exit: Coordenadas ``(x,  y)`` de la salida.
        output_file: Ruta del fichero de salida.
        perfect: Si el laberinto debe ser perfecto.
        seed: Semilla opcional de generación.
        algorithm: Algoritmo de generación.
        theme: Tema de colores ANSI.
        renderer: Renderizador de salida.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = DEFAULT_ALGORITHM
    theme: str = DEFAULT_THEME
    renderer: str = DEFAULT_RENDERER

    @classmethod
    def from_file(cls, path: str | Path) -> "MazeConfig":
        """Carga y valida un fichero de configuración.

        Args:
            path: Ruta del fichero ``KEY=VALUE``.

        Returns:
            La configuración ya validada.

        Raises:
            ConfigError: Si el fichero no existe, no se puede leer o
                contiene algún valor inválido.
        """
        config_path = Path(path)
        try:
            text = config_path.read_text(encoding="utf-8-sig")
        except FileNotFoundError as error:
            raise ConfigError(
                "No se encontró el fichero de configuración: "
                f"{config_path}"
            ) from error
        except UnicodeError as error:
            raise ConfigError(
                "El fichero de configuración no está en UTF-8: "
                f"{config_path}"
            ) from error
        except OSError as error:
            raise ConfigError(
                "No se pudo leer el fichero de configuración "
                f"{config_path}: {error}"
            ) from error
        values = _parse_values(text)
        return _build_config(values)


def _strip_comment(raw_line: str) -> str:
    """Elimina comentarios completos o al final de una línea."""
    line = raw_line.strip()
    if not line or line.startswith("#"):
        return ""
    return line.split("#", 1)[0].strip()


def _parse_int(name: str, raw: str) -> int:
    """Convierte un valor en entero con un error claro."""
    try:
        return int(raw)
    except ValueError as error:
        raise ConfigError(
            f"{name} debe ser un número entero "
            f"(valor recibido: '{raw}')."
        ) from error

def _parse_positive_int(name: str, raw: str) -> int:
    """Convierte un valor en un entero mayor que cero."""
    value = _parse_int(name, raw)
    if value <= 0:
        raise ConfigError(
            f"{name} debe ser mayor que cero "
            f"(valor recibido: {value})."
        )
    return value


def _parse_bool(name: str, raw: str) -> bool:
    """Convierte ``true`` o ``false`` sin distinguir mayúsculas."""
    value = raw.strip().lower()
    if value == "true":
        return True
    if value == "false":
        return False
    raise ConfigError(
        f"{name} debe ser true o false "
        f"(valor recibido: '{raw}')."
    )


def _parse_coordinates(name: str, raw: str) -> tuple[int, int]:
    """Convierte un valor ``x,y`` en una tupla de enteros."""
    parts = raw.split(",")
    if len(parts) != 2:
        raise ConfigError(
            f"{name} debe tener el formato x,y "
            f"(valor recibido: '{raw}')."
        )
    try:
        x = int(parts[0].strip())
        y = int(parts[1].strip())
    except ValueError as error:
        raise ConfigError(
            f"{name} debe tener el formato x,y con números enteros "
            f"(valor recibido: '{raw}')."
        ) from error
    return x, y


def _parse_choice(name: str, raw: str, allowed: tuple[str, ...]) -> str:
    """Normaliza y valida un valor de una lista cerrada."""
    value = raw.strip().lower()
    if value not in allowed:
        options = ", ".join(allowed)
        raise ConfigError(
            f"{name} no válido: '{raw}'. "
            f"Valores permitidos: {options}."
        )
    return value


def _parse_values(text: str) -> dict[str, str]:
    """Extrae las claves y valores del contenido del fichero."""
    values: dict[str, str] = {}
    for number, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line)
        if not line:
            continue
        if line.count("=") == 0:
            raise ConfigError(
                f"Línea {number}: falta el carácter '=' "
                "(el formato debe ser KEY=VALUE)."
            )
        if line.count("=") > 1:
            raise ConfigError(
                f"Línea {number}: debe contener exactamente un '='."
            )
        raw_key, raw_value = line.split("=", 1)
        key = raw_key.strip().upper()
        value = raw_value.strip()
        if not key:
            raise ConfigError(
                f"Línea {number}: la clave no puede estar vacía."
            )
        if key not in KNOWN_KEYS:
            raise ConfigError(f"Línea {number}: clave desconocida '{key}'.")
        if key in values:
            raise ConfigError(f"Línea {number}: clave duplicada '{key}'.")
        if not value:
            raise ConfigError(
                f"Línea {number}: el valor de '{key}' no puede estar vacío."
            )
        values[key] = value
    return values


def _build_config(values: dict[str, str]) -> MazeConfig:
    """Construye la configuración tipada a partir de los valores."""
    missing = [key for key in MANDATORY_KEYS if key not in values]
    if missing:
        lista = ", ".join(missing)
        raise ConfigError(f"Faltan claves obligatorias: {lista}.")
    width = _parse_positive_int("WIDTH", values["WIDTH"])
    height = _parse_positive_int("HEIGHT", values["HEIGHT"])
    entry = _parse_coordinates("ENTRY", values["ENTRY"])
    exit_position = _parse_coordinates("EXIT", values["EXIT"])
    for name, position in (("ENTRY", entry), ("EXIT", exit_position)):
        x, y = position
        if not (0 <= x < width and 0 <= y < height):
            raise ConfigError(
                f"{name} ({x},{y}) está fuera del laberinto "
                f"de {width}x{height}."
            )
    if entry == exit_position:
        raise ConfigError("ENTRY y EXIT deben ocupar celdas distintas.")
    perfect = _parse_bool("PERFECT", values["PERFECT"])
    seed = (
        _parse_int("SEED", values["SEED"])
        if "SEED" in values
        else None#Error, mirar el valor indicado en pydantic y ver si al establecer None pilla automaticamente el valor por defecto, es decir 42.
    )
    algorithm = _parse_choice(
        "ALGORITHM", values.get("ALGORITHM", DEFAULT_ALGORITHM), ALGORITHMS,
    )
    theme = _parse_choice(
        "THEME", values.get("THEME", DEFAULT_THEME), THEME_NAMES,
    )
    renderer = _parse_choice(
        "RENDERER", values.get("RENDERER", DEFAULT_RENDERER), RENDERERS,
    )
    return MazeConfig(
        width=width, height=height, entry=entry, exit=exit_position,
        output_file=values["OUTPUT_FILE"], perfect=perfect, seed=seed,
        algorithm=algorithm, theme=theme, renderer=renderer,
    )
