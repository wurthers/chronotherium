from typing import TYPE_CHECKING, List
from random import randint, randrange
from logging import getLogger

from chronotherium.entities.chronotherium import Chronotherium
from chronotherium.entities.player import Player
from clubsandwich.geom import Point, Size, Rect
from clubsandwich.tilemap import TileMap, CellOutOfBoundsError
from clubsandwich.generators import RandomBSPTree

from chronotherium.tiles.tile import Tile, Empty, FloorTile, Wall, Orientation, StairsUp, StairsDown, Door
from chronotherium.window import MAP_SIZE, VIEW_SIZE, MAP_ORIGIN

if TYPE_CHECKING:
    from chronotherium.scene import GameScene

logger = getLogger()


class Floor(TileMap):

    LEAF_MIN = 4
    ROOM_MIN = 4
    ROOM_MAX = 7

    def __init__(self, origin: Point, size, variance=0):
        super().__init__(size, cell_class=Empty)
        self.size = size
        self.entities = []
        self.room_min = self.ROOM_MIN
        self.room_max = self.ROOM_MAX
        self.leaf_min = self.LEAF_MIN

        self.stairs_up = None
        self.stairs_down = None

        self.bsp_tree = RandomBSPTree(self.size, self.leaf_min)

        self.bounds = Rect(origin, size)
        self.area = self.bounds.with_inset(1)
        self.generate()

    def set_cell(self, tile: Tile):
        try:
            self._cells[tile.point.x][tile.point.y] = tile
            tile.floor = self
        except IndexError:
            logger.info("Setting cell out of bounds!")
            return False

    def get_empty_tiles(self, rect: Rect = None):
        empty_tiles = []
        if rect is not None:
            for point in rect.points:
                if isinstance(self.cell(point), Empty):
                    empty_tiles.append(self.cell(point))
        else:
            for cell in self.cells:
                if isinstance(cell, Empty):
                    empty_tiles.append(cell)

        return empty_tiles

    def get_open_tiles(self, rect: Rect = None):
        open_tiles = []
        if rect is not None:
            for point in rect.points:
                if self.cell(point).open:
                    open_tiles.append(self.cell(point))
        else:
            for cell in self.cells:
                if cell.open:
                    open_tiles.append(cell)

        return open_tiles

    def find_empty_point(self, rect: Rect = None) -> Point:
        empty_tiles = self.get_empty_tiles(rect=rect)
        return empty_tiles[randrange(0, len(empty_tiles))].point

    def find_open_point(self, rect: Rect = None) -> Point:
        open_tiles = self.get_open_tiles(rect=rect)
        return open_tiles[randrange(0, len(open_tiles))].point

    def connect_tiles(self, tile1: Tile, tile2: Tile, doors: bool = True):
        origin = tile1.point
        dest_neighbors = [point for point in tile2.point.neighbors]
        dest = origin.get_closest_point(dest_neighbors)
        for point in origin.points_bresenham_to(dest):
            if isinstance(self.cell(point), Wall):
                if doors:
                    tile = Door(point)
                else:
                    if isinstance(self.cell(point), Door):
                        return
                    else:
                        tile = FloorTile(point)
            else:
                tile = FloorTile(point)
            self.set_cell(tile)

    def generate(self):
        rooms = []
        for leaf in self.bsp_tree.root.leaves:
            room = leaf.rect.get_random_rect(min_size=Size(self.room_min, self.room_min))
            leaf.data['room'] = room
            leaf.data['connected_to_sibling'] = False
            rooms.append(room)
        for room in rooms:
            self.place_room(room)

        for siblings in self.bsp_tree.root.sibling_pairs:
            try:
                room1 = siblings[0].data.get('room')
                room2 = siblings[1].data.get('room')
                if room1 and room2:
                    self.create_hallway(room1, room2)
            except KeyError as err:
                pass

    def create_hallway(self, room1: Rect, room2: Rect) -> None:
        print("INSIDE CREATE HALLWAY")
        tile1 = self.cell(room1.get_random_point())
        tile2 = self.cell(room2.get_random_point())
        self.connect_tiles(tile1, tile2)

        starting_point = next(tile1.point.points_bresenham_to(tile2.point))
        if tile1.point.y - starting_point.y == 0:
            deltas = (Point(-1, 0), Point(1, 0))
        else:
            deltas = (Point(0, -1), Point(0, 1))

        room1_neighbors = []
        room2_neighbors = []

        try:
            room1_neighbors.append(self.cell(tile1.point + deltas[0]))
        except CellOutOfBoundsError:
            pass

        try:
            room1_neighbors.append(self.cell(tile1.point + deltas[1]))
        except CellOutOfBoundsError:
            pass

        try:
            room2_neighbors.append(self.cell(tile2.point + deltas[0]))
        except CellOutOfBoundsError:
            pass

        try:
            room2_neighbors.append(self.cell(tile2.point + deltas[1]))
        except CellOutOfBoundsError:
            pass

        if len(room1_neighbors) > 0 and len(room2_neighbors) > 0:
            self.connect_tiles(room1_neighbors[0], room2_neighbors[0], doors=False)
        if len(room1_neighbors) > 1 and len(room2_neighbors) > 1:
            self.connect_tiles(room1_neighbors[1], room2_neighbors[1], doors=False)

    def get_rect(self) -> Rect:
        width = randint(self.room_min, self.room_max)
        height = randint(self.room_min, self.room_max)
        origin = self.find_empty_point()
        return Rect(origin, Size(width, height))

    # def place_wall(self, point: Point, orientation: Orientation):
    #     if self.area.contains(point):
    #         if isinstance(self.cell(point), Empty):
    #             self.set_cell(Wall(point, orientation))
    #         elif isinstance(self.cell(point), Wall):
    #             try:
    #                 corner_map = {
    #                     (Point(-1, 0), Point(0, -1)): Orientation.BOTTOM_RIGHT,
    #                     (Point(0, -1), Point(1, 0)): Orientation.BOTTOM_LEFT,
    #                     (Point(1, 0), Point(0, 1)): Orientation.TOP_LEFT,
    #                     (Point(0, 1), Point(-1, 0)): Orientation.TOP_RIGHT,
    #                 }
    #                 left_point, up_point, right_point, down_point = point.neighbors
    #                 neighbor_tiles = {
    #                     left_point: self.cell(left_point),
    #                     up_point: self.cell(up_point),
    #                     right_point: self.cell(right_point),
    #                     down_point: self.cell(down_point)
    #                 }
    #                 floors = [point for point in neighbor_tiles if isinstance(neighbor_tiles[point], FloorTile)]
    #                 walls = [point for point in neighbor_tiles if isinstance(neighbor_tiles[point], Wall)]
    #                 if len(floors) == 2 and len(walls) == 2:
    #                     wall_deltas = (walls[0] - point, walls[1] - point)
    #                     try:
    #                         orientation = corner_map[wall_deltas]
    #                     except KeyError:
    #                         return
    #                     self.set_cell(Wall(point, orientation))
    #
    #             except CellOutOfBoundsError:
    #                 pass

    def place_room(self, room: Rect, no_floor: bool = False):
        if not no_floor:
            for point in room.with_inset(1).points:
                self.set_cell(FloorTile(point))

        for point in room.points_top:
            self.set_cell(Wall(point, Orientation.HORIZONTAL))
        for point in room.points_bottom:
            self.set_cell(Wall(point, Orientation.HORIZONTAL))
        for point in room.points_left:
            self.set_cell(Wall(point, Orientation.VERTICAL))
        for point in room.points_right:
            self.set_cell(Wall(point, Orientation.VERTICAL))
        self.set_cell(Wall(room.origin, Orientation.TOP_LEFT))
        self.set_cell(Wall(room.point_top_right, Orientation.TOP_RIGHT))
        self.set_cell(Wall(room.point_bottom_right, Orientation.BOTTOM_RIGHT))
        self.set_cell(Wall(room.point_bottom_left, Orientation.BOTTOM_LEFT))

    def bounds_room(self):
        for point in self.area.points:
            self.set_cell(FloorTile(point))

        self.place_room(self.bounds, no_floor=True)


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
            self.__floors[i] = Floor(self._origin, self._floor_size)
            self.populate_floor(self.__floors[i])

        for index in self.__floors:
            floor = self.__floors.get(index + 1)
            if floor:
                self.place_stairs(index, index + 1)

        for floor in self.__floors.values():
            if floor.stairs_down and floor.stairs_up:
                floor.connect_tiles(floor.stairs_down, floor.stairs_up)

        player_start_tile = self.floor.cell(self.floor.find_open_point())
        self.player = Player(player_start_tile, self, self.scene)
        self.floor.connect_tiles(player_start_tile, self.floor.stairs_up)

        last_floor = self.get_floor(self.FLOORS - 1)
        chronotherium_start_tile = last_floor.cell(last_floor.find_open_point())
        Chronotherium(chronotherium_start_tile, self, self.scene)
        last_floor.connect_tiles(chronotherium_start_tile, last_floor.stairs_down)

    def populate_floor(self, floor, enemy_density=None):
        enemy_density = enemy_density or {}
        for enemy, density in enemy_density.items():

            point = floor.find_open_point()
            enemy(point, self, self.scene)

    def place_stairs(self, floor_index, dest_floor_index):
        floor = self.__floors[floor_index]
        dest_floor = self.__floors[dest_floor_index]

        stairs_point = floor.find_open_point()
        dest_point = dest_floor.find_open_point()

        stairs_up = StairsUp(stairs_point)
        stairs_down = StairsDown(dest_point)
        stairs_up.set_destination(stairs_down, floor_index, dest_floor_index, link=True)

        floor.set_cell(stairs_up)
        dest_floor.set_cell(stairs_down)

        floor.stairs_up = stairs_up
        dest_floor.stairs_down = stairs_down

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

    def find_in_bounds_orthogonal(self, point: Point, delta: int = 1) -> Point:
        to_check = [Point(0, -delta), Point(delta, 0), Point(0, delta), Point(-delta, 0)]
        for check in to_check:
            if self.floor.area.contains(point + check):
                return point + check

    def diagonals(self, point: Point, delta: int = 2) -> List[Point]:
        to_check = [Point(-delta, -delta), Point(delta, delta), Point(delta, -delta), Point(-delta, delta)]
        safe = []
        for check in to_check:
            if self.floor.area.contains(point + check):
                safe.append(point + check)
        return safe

    def move_floors(self, floor: Floor):
        for index, check_floor in self.__floors.items():
            if floor is check_floor:
                self._current_floor = index

    def get_floor(self, index):
        if 0 <= index <= self.FLOORS:
            return self.__floors[index]
        else:
            raise IndexError("Attempted to get a floor that doesn't exist!")

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
