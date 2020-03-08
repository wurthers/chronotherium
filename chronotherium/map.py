from typing import TYPE_CHECKING, List
from random import randint, randrange
from logging import getLogger

from chronotherium.entities.chronotherium import Chronotherium
from chronotherium.entities.golem import Golem
from chronotherium.entities.sentry import Sentry
from chronotherium.entities.knight import Knight
from chronotherium.entities.player import Player
from clubsandwich.geom import Point, Size, Rect
from clubsandwich.tilemap import TileMap, CellOutOfBoundsError
from clubsandwich.generators import RandomBSPTree, BSPNode

from chronotherium.tiles.tile import Tile, Empty, FloorTile, Wall, Orientation, StairsUp, StairsDown, Door
from chronotherium.window import MAP_SIZE, VIEW_SIZE, MAP_ORIGIN

if TYPE_CHECKING:
    from chronotherium.scene import GameScene

logger = getLogger()


class Floor(TileMap):

    LEAF_MIN = 6
    ROOM_MIN = 5
    ROOM_MAX = 7

    def __init__(self, origin: Point, size: Size):
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

    def connect_tiles(self, tile1: Tile, tile2: Tile, doors: bool = True, manhattan: bool = False):
        origin = tile1.point
        dest = origin.get_closest_point([neighbor for neighbor in tile2.point.neighbors])
        self.hallway_tile(origin, doors)
        if manhattan:
            for point in origin.path_L_to(dest):
                self.hallway_tile(point, doors)
        else:
            for point in origin.points_bresenham_to(dest):
                self.hallway_tile(point, doors)
        self.hallway_tile(dest, doors)

    def hallway_tile(self, point, doors=True):
        if isinstance(self.cell(point), Wall):
            if doors:
                if any([neighbor for neighbor in point.neighbors if isinstance(neighbor, Door)]):
                    return
                else:
                    tile = Door(point)
            else:
                if isinstance(self.cell(point), Door):
                    return
                else:
                    tile = FloorTile(point)
        else:
            tile = FloorTile(point)
        self.set_cell(tile)

    def connect_nodes(self, node1: BSPNode, node2: BSPNode, connect_parents: bool = False):
        if not node1.data.get('connected_to_sibling') or not node2.data.get('connected_to_sibling'):
            room1 = node1.data.get('room')
            room2 = node2.data.get('room')
            if room1 and room2:
                self.create_hallway(room1, room2, horiz=node1.is_horz)
            else:
                halls = randint(2, 4)
                for i in range(0, halls):
                    tile1 = self.cell(self.find_open_point(rect=node1.rect.with_inset(1)))
                    tile2 = self.cell(self.find_open_point(rect=node2.rect.with_inset(1)))
                    self.connect_tiles(tile1, tile2)
            node1.data['connected_to_sibling'] = True
            node2.data['connected_to_sibling'] = True
        if connect_parents:
            parent1 = node1.parent_weakref()
            parent2 = node2.parent_weakref()
            if parent1 and parent2:
                self.connect_nodes(parent1, parent2)

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
            self.connect_nodes(*siblings)

        for leaf in self.bsp_tree.root.leaves:
            self.connect_nodes(leaf, next(self.bsp_tree.root.leaves), connect_parents=True)

    def create_hallway(self, room1: Rect, room2: Rect, horiz=False) -> None:

        halls = randint(2, 3)
        for i in range(0, halls):
            if not horiz:
                top = [point for point in room1.points_top]
                edge_point = top[randrange(0, len(top))]
                closest_point = edge_point.get_closest_point([p for p in room2.points])
                if room2.with_inset(1).contains(next(edge_point.path_L_to(closest_point))):
                    bottom = [point for point in room1.points_bottom]
                    edge_point = bottom[randrange(0, len(bottom))]
                    closest_point = edge_point.get_closest_point([p for p in room2.points])
                edge_tile = self.cell(edge_point)
                closest_tile = self.cell(closest_point)
                self.connect_tiles(edge_tile, closest_tile, manhattan=True)
            else:
                right = [point for point in room1.points_right]
                edge_point = right[randrange(0, len(right))]
                closest_point = edge_point.get_closest_point([p for p in room2.points])
                if room2.with_inset(1).contains(next(edge_point.path_L_to(closest_point))):
                    left = [point for point in room1.points_left]
                    edge_point = left[randrange(0, len(left))]
                    closest_point = edge_point.get_closest_point([p for p in room2.points])
                edge_tile = self.cell(edge_point)
                closest_tile = self.cell(closest_point)
                self.connect_tiles(edge_tile, closest_tile, manhattan=True)

    def get_rect(self) -> Rect:
        width = randint(self.room_min, self.room_max)
        height = randint(self.room_min, self.room_max)
        origin = self.find_empty_point()
        return Rect(origin, Size(width, height))

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

    FLOORS = 6
    FLOOR_SIZE = MAP_SIZE
    VIEW_SIZE = VIEW_SIZE
    ORIGIN = MAP_ORIGIN
    ENEMY_DENSITY = 30

    __enemies = [Golem, Sentry, Knight]

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

        player_start_tile = self.floor.cell(self.floor.stairs_up.point.
                                            get_farthest_point([tile.point for tile in self.floor.get_open_tiles()]))
        self.player = Player(player_start_tile, self, self.scene)
        self.floor.connect_tiles(player_start_tile, self.floor.stairs_up)

        last_floor = self.get_floor(self.FLOORS - 1)
        chronotherium_start_tile = last_floor.cell(last_floor.find_open_point())
        Chronotherium(chronotherium_start_tile, self, self.scene)
        last_floor.connect_tiles(chronotherium_start_tile, last_floor.stairs_down)

    def populate_floor(self, floor):
        total_enemies = int(len(floor.get_open_tiles()) / self.ENEMY_DENSITY)
        for enemy in self.__enemies:
            specific_density = enemy.DENSITY
            for i in range(0, int(total_enemies * specific_density)):
                tile = floor.cell(floor.find_open_point())
                enemy(tile, self, self.scene)

    def place_stairs(self, floor_index, dest_floor_index):
        floor = self.__floors[floor_index]
        dest_floor = self.__floors[dest_floor_index]

        if floor.stairs_down:
            stairs_point = floor.stairs_down.point.\
                get_farthest_point([tile.point for tile in self.floor.get_open_tiles()])
        else:
            stairs_point = floor.find_open_point()
        dest_point = dest_floor.find_open_point()

        stairs_up = StairsUp(stairs_point)
        stairs_down = StairsDown(dest_point)
        stairs_up.set_destination(stairs_down, floor_index, dest_floor_index, link=True)

        floor.set_cell(stairs_up)
        dest_floor.set_cell(stairs_down)

        floor.stairs_up = stairs_up
        dest_floor.stairs_down = stairs_down

    def random_open_adjacent(self, point):
        neighbors = []
        for neighbor in point.neighbors:
            try:
                if self.floor.cell(neighbor).open:
                    neighbors.append(neighbor)
            except CellOutOfBoundsError:
                pass
        for neighbor in point.diagonal_neighbors:
            try:
                if self.floor.cell(neighbor).open:
                    neighbors.append(neighbor)
            except CellOutOfBoundsError:
                pass
        if len(neighbors) > 0:
            return neighbors[randrange(0, len(neighbors))]
        else:
            return point

    def closest_open_point(self, point: Point) -> Point:
        neighbors = [neighbor for neighbor in point.neighbors]
        neighbors.extend([neighbor for neighbor in point.diagonal_neighbors])

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
        if delta == 1:
            to_check = point.neighbors
            for check in to_check:
                try:
                    if self.floor.contains_point(check):
                        return check
                except CellOutOfBoundsError:
                    continue
        else:
            to_check = [Point(0, -delta), Point(delta, 0), Point(0, delta), Point(-delta, 0)]

            for check in to_check:
                try:
                    if self.floor.contains_point(point + check):
                        return point + check
                except CellOutOfBoundsError:
                    continue

        # Don't return None, just in case
        return point

    def diagonals(self, point: Point, delta: int = 2) -> List[Tile]:
        to_check = [neighbor for neighbor in point.diagonal_neighbors]
        to_check.extend([Point(-delta, -delta), Point(delta, delta), Point(delta, -delta), Point(-delta, delta)])
        safe = []
        for check in to_check:
            try:
                safe.append(self.floor.cell(point + check))
            except CellOutOfBoundsError:
                pass
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

    def get_allows_light(self, point):
        try:
            return not self.floor.cell(point).block_sight
        except CellOutOfBoundsError:
            return False

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
