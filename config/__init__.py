"""Configuration helpers kept for backward-compatible imports."""

from .MazeConfig import (
    ConfigError, MazeConfigParser, MazeConfig
)

__all__ = ["ConfigError", "MazeConfig", "MazeConfigParser"]
