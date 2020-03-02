from clubsandwich.geom import Point, Size
from clubsandwich.tilemap import TileMap

from chronotherium.tiles.tile import Floor


class Map:

    def __init__(self, floor_size: Size, view_size: Size, origin: Point, center: Point):
        self._floor_size = floor_size
        self._origin = origin
        self._center = center
        self._view_size = view_size

        self.floor = TileMap(floor_size, cell_class=Floor)

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
