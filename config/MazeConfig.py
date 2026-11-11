"""
posibles errores en config.txt,
HEIGH -> La clave no existe, le falta la T del final(esta mal escrita).
_HEIGHT -> DEBERIA SER INCORRECTO YA QUE LA CLAVE _HEIGHT NO EXISTE TAL CUAL(con la barra-baja)
HEIGHT -> La clave esta incompleta al no tener el valor asignado, le falta el = y el valor.
HEIGHT= -> La clave esta incompleta al no tener el valor asignado, le falta el valor.
HEIGHT15 -> La clave tiene mal formato, no es KEY=VALUE, le falta el = entre la clave y el valor.
HEIGHTHEIGHT=15 -> La clave tiene mal formato, no es KEY=VALUE, tiene dos veces la clave y un solo valor.
HEIGHT==15 -> La clave tiene mal formato, no es KEY=VALUE, tiene dos veces el = en la linea.
HEIGHT=           15 -> El valor de la clave ha deser aceptado!
HEIGHT           =15 -> ¿La clave ha deser aceptada?
"""

"""
IV.3 Configuration file format
    The configuration file must contain one ‘KEY=VALUE‘ pair per line.
    Lines starting with # are comments and must be ignored.
    The following keys are mandatory:
        Key         Description                     Example
        WIDTH       Maze width (number of cells)    WIDTH=20
        HEIGHT      Maze height                     HEIGHT=15
        ENTRY       Entry coordinates (x,y)         ENTRY=0,0
        EXIT        Exit coordinates (x,y)          EXIT=19,14
        PERFECT     Is the maze perfect?            PERFECT=True
        OUTPUT_FILE Output filename                 OUTPUT_FILE=maze.txt

    You may add additional keys (e.g., seed, algorithm, display mode) if useful.
    A default configuration file must be available in your Git repository


1.- Se comprueba que el fichero de configuracion exista(file not found).
2.- Se comprueba que el fichero de configuracion tenga la sintaxis correcta(bad syntax).
3.- Una vez se ha comprbado que la sintaxis es correcta, verificamos si los parametros indicados por KEY=VALUE son posibles o no(impossible maze parameters)
4.- Una vez se ha comprbado que los parametros son posibles, verificamos si la configuracion es valida o no(invalid configuration).

You may add additional keys (e.g., seed, algorithm, display mode) if useful.
A default configuration file must be available in your Git repository.
"""

"""Carga y validación del fichero de configuración."""  
from pathlib import Path
from __future__ import annotations
from typing import Any, Final, Optional, override
from pydantic import (
    BaseModel, Field, ConfigDict,
    model_validator, ValidationError
)
from ..themes import (
    MazeThemeEnum, MazeThemeRendererEnum,
    MAZE_THEMES, DEFAULT_THEME,
    RENDERERS, DEFAULT_RENDERER
)


ALGORITHMS: Final[tuple[str, ...]] = (
    "recursive_backtracker", "hunt_and_kill",
)
DEFAULT_ALGORITHM: Final[str] = "recursive_backtracker"# establecer el correcto en caso de rechazar el backtracker.
MANDATORY_KEYS: Final[tuple[str, ...]] = (
    "WIDTH", "HEIGHT", "ENTRY", "EXIT",
    "OUTPUT_FILE", "PERFECT",
)
OPTIONAL_KEYS: Final[tuple[str, ...]] = (
    "SEED", "ALGORITHM", "THEME", "RENDERER",
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


class MazeConfigParser:

    def _strip_comment(self, raw_line: str) -> str:
        """Elimina comentarios completos o al final de una línea."""
        line = raw_line.strip()
        if not line or line.startswith("#"):
            return ""
        return line.split("#", 1)[0].strip()

    def _parse_int(self, name: str, raw: str) -> int:
        """Convierte un valor en entero con un error claro."""
        try:
            return int(raw)
        except ValueError as error:
            raise ConfigError(
                f"{name} debe ser un número entero "
                f"(valor recibido: '{raw}')."
            ) from error

    def _parse_positive_int(self, name: str, raw: str) -> int:
        """Convierte un valor en un entero mayor que cero."""
        value = self._parse_int(name, raw)
        if value <= 0:
            raise ConfigError(
                f"{name} debe ser mayor que cero "
                f"(valor recibido: {value})."
            )
        return value

    def _parse_bool(self, name: str, raw: str) -> bool:
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

    def _parse_coordinates(self, name: str, raw: str) -> tuple[int, int]:
        """Convierte un valor ``x,y`` en una tupla de enteros."""
        parts = raw.split(",")
        if len(parts) != 2:
            raise ConfigError(
                f"{name} debe tener el formato x,y (valor recibido: '{raw}')."
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

    def _parse_choice(self, name: str, raw: str, allowed: tuple[str, ...]) -> str:
        """Normaliza y valida un valor de una lista cerrada."""
        value = raw.strip().lower()
        if value not in allowed:
            options = ", ".join(allowed)
            raise ConfigError(
                f"{name} no válido: '{raw}'. Valores permitidos: {options}."
            )
        return value

    def _parse_config_values(self, text: str) -> dict[str, str]:
        """Extrae las claves y valores del contenido del fichero."""
        config_values: dict[str, str] = {}
        for number, raw_line in enumerate(text.splitlines(), start=1):
            line = self._strip_comment(raw_line)
            if not line:
                continue
            if line.count("=") == 0:
                raise ConfigError(
                    f"Error at line {number}: falta el carácter '=' "
                    "(el formato debe ser KEY=VALUE)."
                )
            if line.count("=") > 1:
                raise ConfigError(
                    f"Error at line {number}: There must be one '=' per line."
                )
            raw_key, raw_value = line.split("=", 1)
            key = raw_key.strip().upper()
            value = raw_value.strip()
            if not key:
                raise ConfigError(
                    f"Error at line {number}: The key can't be empty."
                )
            if key not in KNOWN_KEYS:
                raise ConfigError(
                    f"Error at line {number}: The given key is unknown."
                    f" Has incorrect format: '{key}'."
                )
            if key in config_values:
                raise ConfigError(
                    f"Error at line {number}: "
                    f"The given key is duplicated: '{key}'."
                )
            if not value:
                raise ConfigError(
                    f"Error at line {number}: "
                    f"The value of key '{key}' can't be empty."
                    "There must exist a value parameter."
                )
            config_values[key] = value
        return config_values
    
    def build_config(self, text: str) -> MazeConfig:
        """Construye la configuración tipada a partir de los valores."""
        config_values: dict[str, Any] = self._parse_config_values(text)
        missing = [
            key for key in MANDATORY_KEYS
            if key not in config_values
        ]
        if missing:
            lista = ", ".join(missing)
            raise ConfigError(f"Faltan claves obligatorias: {lista}.")
        width = self._parse_positive_int("WIDTH", config_values["WIDTH"])
        height = self._parse_positive_int("HEIGHT", config_values["HEIGHT"])
        entry = self._parse_coordinates("ENTRY", config_values["ENTRY"])
        exit_position = self._parse_coordinates("EXIT", config_values["EXIT"])
        for name, position in (("ENTRY", entry), ("EXIT", exit_position)):
            x, y = position
            if not (0 <= x < width and 0 <= y < height):
                raise ConfigError(
                    f"{name} ({x},{y}) está fuera del laberinto "
                    f"de {width}x{height}."
                )
        if entry == exit_position:
            raise ConfigError("ENTRY y EXIT deben ocupar celdas distintas.")
        perfect = self._parse_bool("PERFECT", config_values["PERFECT"])
        seed = (
            self._parse_int("SEED", config_values["SEED"])
            if "SEED" in config_values else None
        )
        algorithm = self._parse_choice(
            "ALGORITHM",
            config_values.get("ALGORITHM", DEFAULT_ALGORITHM),
            ALGORITHMS,
        )
        theme = self._parse_choice(
            "THEME",
            config_values.get("THEME", DEFAULT_THEME),
            MAZE_THEMES.keys(),
        )
        renderer = self._parse_choice(
            "RENDERER",
            config_values.get("RENDERER", DEFAULT_RENDERER),
            RENDERERS,
        )
        config_data = {
            "maze_width": width, "maze_height": height, "maze_entry": entry,
            "maze_exit": exit_position, "output_file": config_values["OUTPUT_FILE"],
            "perfect": perfect, "maze_algorithm": algorithm,
            "maze_theme": theme, "maze_renderer_type": renderer,
        }
        if "SEED" in config_values:
            config_data["maze_seed"] = self._parse_int(
                "SEED", config_values["SEED"]
            )
        return config_data
        try:
            return MazeConfig(**config_data)
        except ValidationError as error:
            raise ConfigError(
                f"Invalid configuration: {error}"
            ) from error


class MazeConfig(BaseModel):
    """
    Config class for maze generation and rendering.
    This class uses Pydantic for data validation and type checking.
    Attributes:
        maze_width (int): Width of the maze.
        maze_height (int): Height of the maze.
        maze_entry (tuple[int, int]): Coordinates of the maze entry point (x, y).
        maze_exit (tuple[int, int]): Coordinates of the maze exit point (x, y).
        output_file (str): Output filename for the maze.
        perfect (bool): Indicates if the maze is perfect (no loops).
        maze_seed (Optional[int]): Seed for maze generation.
        maze_algorithm (Optional[str]): Algorithm used for maze generation.
        maze_theme (Optional[str]): Theme used for maze rendering.
        maze_renderer_type (Optional[str]): Renderer used for maze rendering.
    Raises:
        ValueError: If the maze entry or exit points are out of bounds or if they are the same.
        ValueError: If the maze width or height are not positive integers.
        ValueError: If the maze seed is not an integer.
        ValueError: If the maze algorithm is not a valid algorithm.
        ValueError: If the maze theme is not a valid theme.
        ValueError: If the maze renderer is not a valid renderer.
    """
    model_config = ConfigDict(validate_assignment=True)
    maze_width: int = Field(gt=0, description="Width of the maze")
    maze_height: int = Field(gt=0, description="Height of the maze")
    maze_entry: tuple[int, int] = Field(
        min_length=2, max_length=2,
        description="Coordinates of the maze entry point(x,y)"
    )
    maze_exit: tuple[int, int] = Field(
        min_length=2, max_length=2,
        description="Coordinates of the maze exit point(x,y)"
    )
    output_file: str = Field(
        min_length=1, description="Output filename for the maze"
    )
    perfect: bool = Field(
        default=False, description="Indicates if the maze is perfect"
    )
    maze_seed: Optional[int] = Field(
        default=42, description="Seed for maze generation."
    )
    maze_algorithm: Optional[str] = Field(
        default="recursive_backtracker",
        description="Algorithm used for maze generation."
    )
    maze_theme: Optional[MazeThemeEnum] = Field(
        default=DEFAULT_THEME,
        description="Theme used for maze rendering."
    )
    maze_renderer_type: Optional[MazeThemeRendererEnum] = Field(
        default=DEFAULT_RENDERER,
        description="Renderer used for maze rendering."
    )

    @model_validator(mode="after")
    def validate_coordinates(self):
        x, y = self.maze_entry
        if not (0 <= x < self.maze_width and 0 <= y < self.maze_height):
            raise ValueError(
                "Invalid configuration: Maze entry is out of bounds."
            )
        x, y = self.maze_exit
        if not (0 <= x < self.maze_width and 0 <= y < self.maze_height):
            raise ValueError(
                "Invalid configuration: Maze exit is out of bounds."
            )
        if self.maze_entry == self.maze_exit:
            raise ValueError(
                "Invalid configuration: Maze exit can't be the same as entry."
            )
        return self

    @classmethod
    def from_file(cls, path: str | Path) -> "MazeConfig":
        """Carga y valida un fichero de configuración.
        Function that reads valid configuration and
        return a dictionary of configuration config_values for pydantic model.

        Args:
            path: Ruta del fichero ``KEY=VALUE``.
        Returns:
            La configuración ya validada.
        Raises:
            ConfigError: Si el fichero no existe, no se puede leer o
                contiene algún valor inválido.
        Usage:
            maze_config = MazeConfig.from_file("config.txt")
        """
        config_path = Path(path)
        try:
            text = config_path.read_text(encoding="utf-8-sig")
        except FileNotFoundError as error:
            raise ConfigError(
                f"No se encontró el fichero de configuración: {config_path}"
            ) from error
        except UnicodeError as error:
            raise ConfigError(
                f"El fichero de configuración no está en UTF-8: {config_path}"
            ) from error
        except OSError as error:
            raise ConfigError(
                "No se pudo leer el fichero de configuración "
                f"{config_path}: {error}"
            ) from error
        except Exception as error:
            raise ConfigError(
                "Error desconocido al leer el fichero de configuración "
                f"{config_path}: {error}"
            ) from error
        try:
            return cls(**MazeConfigParser().build_config(text))
        except (ConfigError, ValidationError) as error:
            raise ConfigError(
                f"Error en el fichero de configuración {config_path}: {error}"
            ) from error


    def __str__(self):
        return (
            f"Width: {self.maze_width}\n"
            f"Height: {self.maze_height}\n"
            f"Maze Entry: {self.maze_entry}\n"
            f"Maze Exit: {self.maze_exit}\n"
            f"Perfect: {self.perfect}\n"
            f"Output File: {self.maze_output_file}\n"
            f"Seed: {self.maze_seed}\n"
            f"Algorithm: {self.maze_algorithm}\n"
            f"Theme: {self.maze_theme}\n"
            f"Renderer: {self.maze_renderer_type}"
        )
