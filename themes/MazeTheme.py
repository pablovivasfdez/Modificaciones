"""
            Palette
                │
                ▼
            Renderer
        /           \
        /            \
        ▼            ▼
Console-Renderer  MiniLibX-Renderer
    │              │
    ▼              ▼
ANSI/ASCII       pixels


¡¡¡ IMPORTANTE !!!
CUANDO SE VAYA A MOSTRAR UNA CELDA, OBTENEMOS DE MazeCell EL TIPO DE CELDA QUE ES(ColorType.BACKGROUND por ejemplo), YA QUE CON ESE TIPO LUEGO USAMOS
MIDNIGHT_CYBER_PALETTE.get(cell_type) Y SE DEBE MOSTRAR EL COLOR HEXADECIMAL OBTENIDO CON EL get().
"""
from __future__ import annotations
from .Themes import (
    MazeThemePalette, RESET, MAZE_THEMES,
    DEFAULT_THEME, DEFAULT_RENDERER
)


class MazeTheme():
    """Identifiers for the available maze themes."""
    def __init__(
        self, renderer_type: str = DEFAULT_RENDERER,
        maze_theme: str = DEFAULT_THEME#: MazeThemeRendererEnum | None
    ):
        self.theme_name = maze_theme
        self.renderer_type = renderer_type
    """renderer_type: str = "minilibx"  # Default renderer type
    maze_theme: MazeThemePalette = "midnight"""

    def get_maze_theme(self, theme_name: str) -> MazeThemePalette:
        """Return a palette by its identifier."""
        try:
            return MAZE_THEMES.get(theme_name.lower()).get(self.renderer_type)
        except KeyError:
            available = ", ".join(MAZE_THEMES)
            raise ValueError(
                f"Unknown palette '{theme_name}'. "
                f"Available maze themes: {available}"
            )

    @property
    def theme_name(self) -> str:
        """Return the name of the current maze theme."""
        return self.theme_name

    def set_theme_name(self, new_theme_name: str) -> None:
        """Set a new maze theme name."""
        self.theme_name = new_theme_name

    @property
    def theme_renderer(self) -> str:
        """Return the renderer type of the current maze theme."""
        return self.renderer_type

    def set_theme_renderer(self, new_renderer_type: str) -> None:
        """Set a new renderer type for the maze theme."""
        self.renderer_type = new_renderer_type

    """ CUANDO USARLO: EL THEME PUEDE ESTAR EN MODO MANUAL,
        DONDE SOLOCAMBIA CUANDO SE INDICA EN EL MENU,
        O AUTOMATICO, DONDE CADA VISUALIZACION SE USA ESTA FUNCION PARA OBTENER EL SIGUIENTE Y USARLO.
    """
    def next_theme(self, name: str) -> str:
        """Devuelve el siguiente tema de la lista, de forma circular."""
        try:
            index = MAZE_THEMES.keys().index(name.lower())
        except ValueError:
            index = -1
        return MAZE_THEMES.keys()[(index + 1) % len(MAZE_THEMES)]

    def paint_ansi(self, text: str, color: int, enabled: bool) -> str:
        """Aplica un color ANSI al texto si los colores están activos."""
        if not enabled:
            return text
        return f"\x1b[38;5;{color}m{text}{RESET}"
