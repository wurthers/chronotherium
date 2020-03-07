from typing import TYPE_CHECKING, Optional
from random import randrange
from logging import getLogger

from clubsandwich.geom import Point, Size, Rect
from clubsandwich.tilemap import TileMap, CellOutOfBoundsError

from chronotherium.tiles.tile import Tile, Empty, FloorTile, Wall, Orientation
from chronotherium.window import MAP_SIZE, VIEW_SIZE, MAP_ORIGIN

if TYPE_CHECKING:
    from chronotherium.scene import GameScene

logger = getLogger()


class Floor(TileMap):
    def __init__(self, size, variance=0):
        super().__init__(size, cell_class=Empty)
        self.size = size
        self.variance = variance
        self.entities = []

        if self.variance != 0:
            width = randrange(self.size.width - self.variance, self.size.width + self.variance)
            height = randrange(self.size.height - self.variance, self.size.width + self.variance)
        else:
            width = self.size.width
            height = self.size.height
        self.bounds = Rect(Point(0, 0), Size(width, height))
        self.area = self.bounds.with_inset(1)

        self.stairs_down = None
        self.stairs_up = None

    def set_cell(self, tile: Tile):
        try:
            self._cells[tile.point.x][tile.point.y] = tile
        except IndexError:
            logger.debug("Setting cell out of bounds!")
            return False

    def carve_floor(self):
        for point in self.area.points:
            self.set_cell(FloorTile(point))

        self.set_cell(Wall(self.bounds.origin, Orientation.TOP_LEFT))
        self.set_cell(Wall(self.bounds.point_top_right, Orientation.TOP_RIGHT))
        self.set_cell(Wall(self.bounds.point_bottom_right, Orientation.BOTTOM_RIGHT))
        self.set_cell(Wall(self.bounds.point_bottom_left, Orientation.BOTTOM_LEFT))
        for point in self.bounds.points_top:
            self.set_cell(Wall(point, Orientation.HORIZONTAL))
        for point in self.bounds.points_bottom:
            self.set_cell(Wall(point, Orientation.HORIZONTAL))
        for point in self.bounds.points_left:
            self.set_cell(Wall(point, Orientation.VERTICAL))
        for point in self.bounds.points_right:
            self.set_cell(Wall(point, Orientation.VERTICAL))


class Map:

    FLOORS = 5
    FLOOR_SIZE = MAP_SIZE
    VIEW_SIZE = VIEW_SIZE
    ORIGIN = MAP_ORIGIN

    def __init__(self, scene: 'GameScene'):

        self.__floors = {}

        self._floor_size = self.FLOOR_SIZE
        self._origin = self.ORIGIN
        self._center = Point(int(self._floor_size.width / 2), int(self._floor_size.height / 2))
        
        self._view_size = self.VIEW_SIZE
        self._view_rect = Rect(self._origin, self._view_size)
        self._view_center = Point(int(self._view_size.width / 2), int(self._view_size.height / 2))
        
        self._current_floor = 0
        
        self.scene = scene

        for i in range(0, self.FLOORS):
            self.__floors[i] = self.generate_floor()
            self.populate_floor(self.__floors[i])

    def generate_floor(self) -> Floor:
        floor = Floor(self._floor_size)
        floor.carve_floor()
        return floor

    def populate_floor(self, floor, enemy_density=None):
        enemies = []
        enemy_density = enemy_density or {}
        for enemy, density in enemy_density.items():

            point = self.find_open_point(floor)
            enemies.append(enemy(point, self, self.scene))

        floor.entities.extend(enemies)
        return enemies

    def closest_open_point(self, point: Point) -> Point:
        neighbors = point.neighbors
        found = None
        for neighbor in neighbors:
            if self.floor.cell(neighbor).open:
                found = neighbor
        if found is None:
            for neighbor in neighbors:
                found = self.closest_open_point(neighbor)
                if found is not None:
                    return found
        return found

    def find_open_point(self, floor: Optional[Floor] = None) -> Point:
        if floor is None:
            floor = self.floor
        while True:
            point = floor.area.get_random_point()
            try:
                found = True
                if floor.cell(point).block or not floor.cell(point).open:
                    found = False
                if found:
                    return point
            except CellOutOfBoundsError:
                pass
            continue

    def find_in_bounds_orthogonal(self, point: Point, delta: int = 1) -> Point:
        to_check = [Point(0, -delta), Point(delta, 0), Point(0, delta), Point(-delta, 0)]
        for check in to_check:
            if self.floor.area.contains(point + check):
                return point + check

    def diagonals(self, point: Point, delta: int = 2) -> Point:
        to_check = [Point(-delta, -delta), Point(delta, delta), Point(delta, -delta), Point(-delta, delta)]
        safe = []
        for check in to_check:
            if self.floor.area.contains(point + check):
                safe.append(point + check)
        return safe

    @property
    def floor(self):
        return self.__floors[self._current_floor]

    @property
    def current_floor(self):
        return self._current_floor

    @property
    def floor_size(self):
        return self._floor_size

    @property
    def origin(self):
        return self._origin

    @property
    def center(self):
        return self._center

    @property
    def view_size(self):
        return self._view_size

    @property
    def view_rect(self):
        return self._view_rect

    @property
    def view_center(self):
        return self._view_center
