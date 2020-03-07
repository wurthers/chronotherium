from typing import TYPE_CHECKING
from enum import Enum

from clubsandwich.geom import Point

from .entity import Actor, EntityType, ActorType
from chronotherium.map import Map

if TYPE_CHECKING:
    from chronotherium.scene import GameScene


class Player(Actor):

    class Skills(Enum):
        REWIND = "rewind"
        FREEZE = "freeze"
        PUSH = "push"
        DIAGONAL = "diagonal"

    __levels = {
        1: 15,
        2: 35,
        3: 55,
        4: 75
    }

    __skills = {
        0: Skills.REWIND,
        2: Skills.FREEZE,
        3: Skills.PUSH,
        4: Skills.DIAGONAL
    }

    NAME = "Player"
    TYPE = EntityType.PLAYER
    GLYPH = ActorType.PLAYER
    BASE_HP = 10
    BASE_TP = 10
    REWIND_LIMIT = 2
    REWIND_COST = 3
    FREEZE_COST = 1
    PUSH_COST = 1
    PUSH_DAMAGE = 1
    DIAGONAL_COST = 4
    DIAGONAL_DAMAGE = 3
    HEAL_RATE = 15

    def __init__(self, position: Point, map: Map, scene: 'GameScene'):
        super().__init__(position, map, scene)
        self._rewind_limit = self.REWIND_LIMIT
        self._rewind_cost = self.REWIND_COST
        self._freeze_cost = self.FREEZE_COST
        self._push_cost = self.PUSH_COST
        self._push_damage = self.PUSH_DAMAGE
        self._heal_clock = 0
        self._heal_rate = self.HEAL_RATE
        self._diagonal_cost = self.DIAGONAL_COST
        self._diagonal_damage = self.DIAGONAL_DAMAGE

        self._found_boss = False
        self.__skills = {}

    def turn(self):
        if self.hp < self.max_hp:
            self._heal_clock += 1
            if self._heal_clock % self._heal_rate == 0:
                self.delta_hp += 1
                self._heal_clock = 0
        super().turn()

    @property
    def max_hp(self):
        return self._max_hp + self.level * 2

    @property
    def max_tp(self):
        return self._max_tp + self.level

    @property
    def rewind_limit(self):
        return self._rewind_limit + self.level

    @property
    def rewind_cost(self):
        return self._rewind_cost - int(self.level / 2)

    @property
    def freeze_cost(self):
        return self._freeze_cost

    @property
    def push_cost(self):
        return self._push_cost

    @property
    def push_damage(self):
        return self._push_damage + int(self.level / 3)

    @property
    def bump_damage(self):
        return self._bump_damage + int(self.level / 4)

    @property
    def diagonal_cost(self):
        return self._diagonal_cost

    @property
    def diagonal_damage(self):
        return self._diagonal_damage

    @property
    def level(self):
        level = 0
        for lvl, xp in self.__levels.items():
            if self._xp > xp:
                level = lvl
        return level
