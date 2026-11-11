from typing import Final
from enum import StrEnum
from dataclasses import dataclass


class ColorType(StrEnum):
    """Types of colors used to render the maze."""
    """Legacy names for the colour slots of a theme."""
    SEED = "seed"
    WALL = "wall"
    OUTER = "outer"
    FLOOR = "floor"
    BACKGROUND = "background"
    END = "end"
    START = "start"
    PATH = "path"


# Los objetos creados con esa clase son inmutables: una vez creados, no puedes modificar sus atributos.
# Si en el menu hay que modificar themes habria que establecerlo en False o buscar otra frorma.
@dataclass(frozen=True)
class MazeThemePalette:
    """Color palette used to render a maze."""
    """Colores ANSI (índice de 256 colores) de un tema."""

    name: str
    seed: str
    wall: str
    outer: str
    floor: str
    background: str
    end: str
    start: str
    path: str

    def get(self, color_type: ColorType) -> str:
        """Return the hexadecimal color for a given color type."""
        return getattr(self, color_type.value)


class MazeThemeEnum(StrEnum):
    """List of available maze themes."""
    MIDNIGHT_CYBER = "midnight"
    OBSIDIAN_NEON = "obsidian"
    ARCTIC_42 = "artic"
    SOLAR_POP = "solar"
    OCEAN_42 = "ocean"
    SYNTHWAVE_42 = "synthwave"

class MazeThemeRendererEnum(StrEnum):
    """List of available maze renderers."""
    TERMINAL = "terminal"
    MINILIBX = "minilibx"

MIDNIGHT_CYBER_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Midnight Cyber",
    background="#0B1020",
    outer="#151B2E",
    floor="#111827",
    wall="#00E5FF",
    seed="#7C3AED",
    start="#22C55E",
    end="#F59E0B",
    path="#A78BFA",# si violeta-suave no sirve, probar con -> Rosa-Neon(#F472B6), Cian-Claro(#67E8F9), Púrpura-Brillante(#C084FC)
)
OBSIDIAN_NEON_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Obsidian Neon",
    background="#09090B",
    outer="#18181B",
    wall="#22C55E",
    floor="#111113",
    seed="#F59E0B",
    start="#06B6D4",
    end="#EF4444",
    path="#E879F9",# si magenta-electrico no sirve, probar con Blanco-Plateado(#E4E4E7)
)
ARCTIC_42_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Arctic 42",
    background="#F8FAFC",
    outer="#E2E8F0",
    floor="#FFFFFF",
    wall="#2563EB",
    seed="#06B6D4",
    start="#16A34A",
    end="#DC2626",
    path="#7C3AED",# si violeta-intensio no sirve, probar con -> Magenta(#C026D3), VerdeAzuladoOscuro(#0F766E), GrisAzuladoOscuro(#475569)
)
SOLAR_POP_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Solar Pop",
    background="#FFF7ED",
    outer="#FED7AA",
    floor="#FFFBEB",
    wall="#EA580C",
    seed="#7C3AED",
    start="#16A34A",
    end="#DC2626",
    path="#2563EB",# si azul-intenso no sirve, probar con -> Cian-Oscuro(#0891B2), Indigo-Electrico(#4F46E5), VerdeAzuladoOscuro(#0F766E)
)
OCEAN_42_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Ocean 42",
    background="#071E26",
    outer="#0B3C49",
    floor="#0F172A",
    wall="#22D3EE",
    seed="#38BDF8",
    start="#2DD4BF",
    end="#FB7185",
    path="#FACC15",# si amarillo-dorado no sirve, probar con -> Violeta luminoso(#C084FC), Naranja coral(#FB923C), Blanco azulado(#E2E8F0)
)
SYNTHWAVE_42_PALETTE: Final[MazeThemePalette] = MazeThemePalette(
    name="Synthwave 42",
    background="#120A1F",
    outer="#2A1638",
    floor="#1B1030",
    wall="#FF2BD6",
    seed="#7C3AED",
    start="#00F5D4",
    end="#FF6B35",
    path="#FDE047",# si amarillo-neon no sirve, probar con -> VerdeLimaNeón(#A3FF12), Blanco(#FFFFFF), Magenta-Eléctrico(#FF4DFF)
)
RESET: Final[str] = "\x1b[0m"
MAZE_THEMES:  Final[dict[str, dict[str, MazeThemePalette]]] = {
    "midnight": {
        "minilibx": MIDNIGHT_CYBER_PALETTE,
        "terminal": MazeThemePalette("midnight", 51, 46, 226, 201, 231),
    },
    "obsidian": {
        "minilibx": OBSIDIAN_NEON_PALETTE,
        "terminal": MazeThemePalette("obsidian", 46, 51, 196, 226, 255),
    },
    "arctic": {
        "minilibx": ARCTIC_42_PALETTE,
        "terminal": MazeThemePalette("arctic", 33, 34, 160, 45, 220),
    },
    "solar": {
        "minilibx": SOLAR_POP_PALETTE,
        "terminal": MazeThemePalette("solar", 208, 34, 160, 129, 220),
    },
    "ocean": {
        "minilibx": OCEAN_42_PALETTE,
        "terminal": MazeThemePalette("ocean", 45, 49, 203, 81, 231),
    },
    "synthwave": {
        "minilibx": SYNTHWAVE_42_PALETTE,
        "terminal": MazeThemePalette("synthwave", 200, 51, 208, 129, 231),
    }
}
DEFAULT_THEME: Final[str] = MazeThemeEnum.MIDNIGHT_CYBER
RENDERERS: Final[tuple[MazeThemeRendererEnum, ...]] = (MazeThemeRendererEnum.TERMINAL, MazeThemeRendererEnum.MINILIBX)
DEFAULT_RENDERER: Final[MazeThemeRendererEnum] = MazeThemeRendererEnum.TERMINAL