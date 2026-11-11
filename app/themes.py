"""Paletas ANSI usadas por el renderizador de terminal."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

RESET: Final[str] = "\x1b[0m"
DEFAULT_THEME: Final[str] = "midnight"


@dataclass(frozen=True)
class Theme:
    """Colores ANSI (índice de 256 colores) de un tema."""

    name: str
    wall: int
    entry: int
    exit: int
    pattern: int
    path: int


THEMES: Final[dict[str, Theme]] = {
    "midnight": Theme("midnight", 51, 46, 226, 201, 231),
    "obsidian": Theme("obsidian", 46, 51, 196, 226, 255),
    "arctic": Theme("arctic", 33, 34, 160, 45, 220),
    "solar": Theme("solar", 208, 34, 160, 129, 220),
    "ocean": Theme("ocean", 45, 49, 203, 81, 231),
    "synthwave": Theme("synthwave", 200, 51, 208, 129, 231),
}

THEME_NAMES: Final[tuple[str, ...]] = tuple(THEMES)


def get_theme(name: str) -> Theme:
    """Devuelve el tema solicitado.

    Raises:
        ValueError: Si el nombre del tema no existe.
    """
    theme = THEMES.get(name.lower())
    if theme is None:
        disponibles = ", ".join(THEME_NAMES)
        raise ValueError(
            f"Tema desconocido: '{name}'. "
            f"Temas disponibles: {disponibles}."
        )
    return theme


def next_theme(name: str) -> str:
    """Devuelve el siguiente tema de la lista, de forma circular."""
    try:
        index = THEME_NAMES.index(name.lower())
    except ValueError:
        index = -1
    return THEME_NAMES[(index + 1) % len(THEME_NAMES)]


def paint(text: str, color: int, enabled: bool) -> str:
    """Aplica un color ANSI al texto si los colores están activos."""
    if not enabled:
        return text
    return f"\x1b[38;5;{color}m{text}{RESET}"
