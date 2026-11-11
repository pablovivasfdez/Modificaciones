"""Colour theme helpers kept for backward-compatible imports."""
"""Compatibility exports for the terminal colour themes."""
from .Themes import (
    ColorType, MazeThemeEnum,
    MazeThemeRendererEnum, RESET,
    DEFAULT_THEME, MAZE_THEMES,
    RENDERERS, DEFAULT_RENDERER
)
from .MazeTheme import MazeTheme

__all__ = [
    "ColorType",
    "MazeThemeEnum",
    "MazeThemeRendererEnum",
    "RESET",
    "DEFAULT_THEME",
    "MAZE_THEMES",
    "RENDERERS",
    "DEFAULT_RENDERER",
    "MazeTheme"
]