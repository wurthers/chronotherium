from clubsandwich.tilemap import Cell
from clubsandwich.geom import Point
from clubsandwich.blt.context import BearLibTerminalContext as Context

from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC

from chronotherium.window import Window, Color

if TYPE_CHECKING:
    from chronotherium.map import Floor


class Terrain(Enum):
    FLOOR = 0x002E          # .
    EMPTY = 0x0020          # SP
    STAIRS_DOWN = 0x003E    # >
    STAIRS_UP = 0x003C      # <
    DOOR = 0x002B           # +
    DOOR_OPEN = 0x002D      # -


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
    TERRAIN = None

    window = Window()

    def __init__(self, point: Point):
        super().__init__(point)
        self._block = self.BLOCK
        self._block_sight = self.BLOCK_SIGHT
        self.color = self.COLOR if self.COLOR is not None else self.window.fg_color
        self._open = self.OPEN
        self.terrain = self.TERRAIN
        self._floor = None

        self.entities = []

    def draw_tile(self, context: Context):
        context.color(self.color)
        context.put(self.point, self.glyph)
        context.color(self.window.fg_color)

    @property
    def floor(self):
        return self._floor

    @floor.setter
    def floor(self, value: 'Floor'):
        self._floor = value

    @property
    def glyph(self):
        return self.terrain.value

    @property
    def block(self):
        return self._block or any(entity.blocking for entity in self.entities)

    @property
    def block_sight(self):
        return self._block_sight

    @property
    def occupied(self):
        return len(self.entities) > 0

    @property
    def open(self):
        return self._open or not self.block

    def interact(self):
        pass


class Empty(Tile):
    OPEN = False
    BLOCK = True
    BLOCK_SIGHT = True
    TERRAIN = Terrain.EMPTY


class FloorTile(Tile):
    TERRAIN = Terrain.FLOOR


class Stairs(Tile, ABC):
    OPEN = False

    def __init__(self, point: Point):
        super().__init__(point)
        self.dest_tile = None
        self._dest_floor_index = None
        self._floor_index = None

    @property
    def floor_index(self):
        return self._floor_index

    def interact(self) -> 'Stairs':
        return self.dest_tile

    def set_destination(self, dest: 'Stairs', floor_index: int, dest_floor_index: int, link: bool = False) -> None:
        self.dest_tile = dest
        self._floor_index = floor_index
        self._dest_floor_index = dest_floor_index

        if link:
            dest.set_destination(self, dest_floor_index, floor_index, link=False)


class StairsUp(Stairs):
    TERRAIN = Terrain.STAIRS_UP


class StairsDown(Stairs):
    TERRAIN = Terrain.STAIRS_DOWN


class Wall(Tile):
    COLOR = Color.CYAN
    OPEN = False
    BLOCK = True
    BLOCK_SIGHT = True

    def __init__(self, point, orientation=Orientation.VERTICAL):
        super().__init__(point)
        self.terrain = orientation


class Door(Tile):
    COLOR = Color.CYAN
    OPEN = False
    BLOCK = True
    BLOCK_SIGHT = True
    TERRAIN = Terrain.DOOR

    def __init__(self, point):
        super().__init__(point)
        self._door_open = False

    def interact(self):
        if not self.occupied:
            self._door_open = False if self._door_open else True
            self._block = False if self._door_open else True
            return True
        return False

    @property
    def glyph(self):
        return Terrain.DOOR_OPEN.value if self._door_open else Terrain.DOOR.value

    @property
    def block(self):
        return self._block or any(entity.blocking for entity in self.entities)

    @property
    def block_sight(self):
        return self._block

    @property
    def door_open(self):
        return self._door_open
