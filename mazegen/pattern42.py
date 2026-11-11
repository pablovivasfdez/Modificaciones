from __future__ import annotations
from dataclasses import dataclass

Position = tuple[int, int]


#El present creo que no haria falta porque si cells es none simplemente el generador podria seguir igual sin hacer nada ya que no habrian celdas "protegidas"
@dataclass
class Pattern42Placement:
    #El resultado
    cells: frozenset[Position]
    present: bool
    warning: str | None = None


class Pattern42Placer:

    GLYPH_WIDTH: int = 7
    GLYPH_HEIGHT: int = 5
    MIN_WIDTH: int = 9
    MIN_HEIGHT: int = 7

    LOGO_POSITIONS: tuple[Position, ...] = (
        (-1, 0), (-2, 0), (-3, 0), (-3, -1), (-3, -2), (-1, 1), (-1, 2), (-1, -1), (-1, -2),
        (1, 0), (2, 0), (3, 0), (3, -1), (3, - 2), (2, -2), (1, -2),
        (1, 1), (1, 2), (2, 2), (3, 2)
    )

    @classmethod
    def place(
        cls,
        width: int,
        height: int,
        entry: Position,
        exit: Position,
        enabled: bool = True,
    ) -> Pattern42Placement:

        if not enabled:
            return Pattern42Placement(frozenset(), False, None)
        if width < cls.MIN_WIDTH or height < cls.MIN_HEIGHT:
            return Pattern42Placement(
                frozenset(),
                False,
                "El patrón 42 se omite: el laberinto debe medir al menos "
                "9x7 celdas.",
            )

        cells: set[Position] = set()
        middlex, middley = width // 2, height // 2
        for dx, dy in cls.LOGO_POSITIONS:
            x, y = middlex + dx, middley + dy
            if (0 <= x < width and 0 <= y < height):
                cells.add((x, y))
        if entry in cells or exit in cells:
            return Pattern42Placement(
                frozenset(cells), False, None
            )
        return Pattern42Placement(
            frozenset(cells), True, None
        )