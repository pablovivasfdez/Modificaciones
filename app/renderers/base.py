"""Interfaz común para los renderizadores de laberintos."""

from __future__ import annotations

from typing import Protocol

from mazegen import Maze


class Renderer(Protocol):
    """Contrato que debe cumplir cualquier renderizador de laberintos."""

    def render(
        self,
        maze: Maze,
        show_path: bool = False,
        theme_name: str = "midnight",
    ) -> str:
        """Devuelve una representación textual del laberinto."""
        ...
