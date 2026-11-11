"""Renderizadores de laberintos disponibles en la aplicación."""

from .base import Renderer
from .console import ConsoleRenderer

__all__ = ["Renderer", "ConsoleRenderer"]
