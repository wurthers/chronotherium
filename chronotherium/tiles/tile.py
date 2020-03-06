from clubsandwich.tilemap import Cell
from clubsandwich.geom import Point
from clubsandwich.blt.context import BearLibTerminalContext as Context

from enum import Enum
from abc import ABC

from chronotherium.window import Window, Color


class Terrain(Enum):
    FLOOR = 0x002E          # .
    EMPTY = 0x0020          # SP
    STAIRS_DOWN = 0x003E    # >
    STAIRS_UP = 0x003C      # <


class Orientation(Enum):
    HORIZONTAL = 0x2500     # ─
    VERTICAL = 0x2502       # │
    TOP_LEFT = 0x250C       # ┌
    TOP_RIGHT = 0x2510      # ┐
    BOTTOM_LEFT = 0x2514    # └
    BOTTOM_RIGHT = 0x2518   # ┘


class Tile(Cell, ABC):

    COLOR = None
    OPEN = True
    BLOCK_SIGHT = False
    BLOCK = False

    window = Window()

    def __init__(self, point: Point):
        super().__init__(point)
        self._block = self.BLOCK
        self._block_sight = self.BLOCK_SIGHT
        self.color = self.COLOR if self.COLOR is not None else self.window.fg_color
        self._open = self.OPEN

        self.glyph = None
        self.occupied_by = []

    def draw_tile(self, context: Context):
        context.color(self.color)
        context.put(self.point, self.glyph)
        context.color(self.window.fg_color)

    @property
    def block(self):
        return self._block or any(entity.blocking for entity in self.occupied_by)

    @property
    def occupied(self):
        return len(self.occupied_by) > 0

    @property
    def open(self):
        return self._open or self.block
    


class Empty(Tile):

    OPEN = False
    BLOCK = True

    def __init__(self, point):
        super().__init__(point)
        self.terrain = Terrain.EMPTY
        self.glyph = self.terrain.value


class FloorTile(Tile):
    def __init__(self, point):
        super().__init__(point)
        self.terrain = Terrain.FLOOR
        self.glyph = self.terrain.value


class Stairs(Tile):

    OPEN = False

    def __init__(self, point):
        super().__init__(point)
        self.terrain = Terrain.STAIRS_UP
        self.glyph = self.terrain.value


class Wall(Tile):

    COLOR = Color.CYAN
    OPEN = False
    BLOCK = True
    BLOCK_SIGHT = True

    def __init__(self, point, orientation=None):
        super().__init__(point)
        self.terrain = orientation if orientation is not None else Orientation.VERTICAL
        self.glyph = self.terrain.value
