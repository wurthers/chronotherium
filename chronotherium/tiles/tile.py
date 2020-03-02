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
    def __init__(self, point: Point, color=None):
        super().__init__(point)
        self.glyph = None
        self.block = False
        self.block_sight = False
        self.window = Window()
        self.color = color if color else self.window.fg_color
        self.open = True
        self.occupied = False
        self.occupied_by = []

    def draw_tile(self, context: Context):
        context.color(self.color)
        context.put(Point(self.point.x, self.point.y), self.glyph)
        context.color(self.window.fg_color)


class Empty(Tile):
    def __init__(self, point):
        super().__init__(point)
        self.open = False
        self.terrain = Terrain.EMPTY
        self.glyph = self.terrain.value
        self.block = True


class Floor(Tile):
    def __init__(self, point, color=None):
        super().__init__(point, color=color)
        self.terrain = Terrain.FLOOR
        self.glyph = self.terrain.value


class Stairs(Tile):
    def __init__(self, point, terrain, color=None):
        super().__init__(point, color=color)
        self.open = False
        self.terrain = Terrain.STAIRS_UP
        self.glyph = self.terrain.value


class Wall(Tile):
    def __init__(self, point, orientation, color=Color.TAN.value):
        super().__init__(point, color=color)
        self.open = False
        self.terrain = orientation
        self.glyph = self.terrain.value
        self.block = True
        self.block_sight = True
