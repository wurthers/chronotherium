from clubsandwich.geom import Point

from .entity import Actor, EntityType
from chronotherium.map import Map


class Player(Actor):

    NAME = "Player"
    TYPE = EntityType.PLAYER
    BASE_HP = 10
    BASE_TP = 5
    REWIND_LIMIT = 3
    REWIND_COST = 2

    def __init__(self, position: Point, map: Map):
        super().__init__(position, map)
        self._rewind_limit = self.REWIND_LIMIT
        self.rewind_cost = self.REWIND_COST

    @property
    def rewind_limit(self):
        return self._rewind_limit
