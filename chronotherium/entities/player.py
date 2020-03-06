from typing import TYPE_CHECKING

from clubsandwich.geom import Point

from .entity import Actor, EntityType, ActorType
from chronotherium.map import Map

if TYPE_CHECKING:
    from chronotherium.scene import GameScene


class Player(Actor):

    __levels = {
        1: 15,
        2: 35,
        3: 55,
        4: 75
    }

    NAME = "Player"
    TYPE = EntityType.PLAYER
    GLYPH = ActorType.PLAYER
    BASE_HP = 10
    BASE_TP = 10
    REWIND_LIMIT = 2
    REWIND_COST = 3

    def __init__(self, position: Point, map: Map, scene: 'GameScene'):
        super().__init__(position, map, scene)
        self._rewind_limit = self.REWIND_LIMIT
        self._rewind_cost = self.REWIND_COST

    @property
    def max_hp(self):
        return self._max_hp + self.level * 2

    @property
    def rewind_limit(self):
        return self._rewind_limit + self.level

    @property
    def rewind_cost(self):
        return self._rewind_cost - int(self.level / 2)

    @property
    def level(self):
        level = 0
        for lvl, xp in self.__levels.items():
            if self._xp > xp:
                level = lvl
        return level
