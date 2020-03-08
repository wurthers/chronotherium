from typing import TYPE_CHECKING
from enum import Enum
from abc import ABC

from chronotherium.tiles.tile import Tile
from chronotherium.entities.entity import Actor, EntityType, ActorType

if TYPE_CHECKING:
    from chronotherium.scene import GameScene
    from chronotherium.map import Map


class SkillType(Enum):
    REWIND = "rewind"
    FREEZE = "freeze"
    PUSH = "push"
    DIAGONAL = "diagonal"


class Skill(ABC):
    LEVEL = 0
    NAME = ''
    KEY = None


class Teleport(Skill):
    LEVEL = 0
    NAME = 'Teleport'
    KEY = 't'


class Rewind(Skill):
    LEVEL = 1
    NAME = 'Rewind'
    KEY = 'r'


class Freeze(Skill):
    LEVEL = 2
    NAME = 'Freeze'
    KEY = 'f'


class Push(Skill):
    LEVEL = 3
    NAME = 'Wormhole'
    KEY = 'p'


class Diagonal(Skill):
    LEVEL = 4
    NAME = 'Event Horizon'
    KEY = 'e'


class Player(Actor):

    __levels = {
        1: {'xp': 10, 'skill': Rewind},
        2: {'xp': 21, 'skill': Freeze},
        3: {'xp': 34, 'skill': Push},
        4: {'xp': 50, 'skill': Diagonal}
    }

    __skills = [Teleport]

    NAME = "Player"
    TYPE = EntityType.PLAYER
    GLYPH = ActorType.PLAYER
    RANGE = 8
    BASE_HP = 10
    BASE_TP = 10
    TELEPORT_COST = 2
    REWIND_LIMIT = 2
    REWIND_COST = 3
    FREEZE_COST = 1
    FREEZE_DAMAGE = 1
    PUSH_COST = 2
    PUSH_DAMAGE = 2
    DIAGONAL_COST = 5
    DIAGONAL_DAMAGE = 4
    HEAL_RATE = 20

    def __init__(self, tile: Tile, map: 'Map', scene: 'GameScene'):
        super().__init__(tile, map, scene)
        self._rewind_limit = self.REWIND_LIMIT
        self._rewind_cost = self.REWIND_COST
        self._freeze_cost = self.FREEZE_COST
        self._freeze_damage = self.FREEZE_DAMAGE
        self._push_cost = self.PUSH_COST
        self._push_damage = self.PUSH_DAMAGE
        self._heal_clock = 0
        self._heal_rate = self.HEAL_RATE
        self._diagonal_cost = self.DIAGONAL_COST
        self._diagonal_damage = self.DIAGONAL_DAMAGE
        self._teleport_cost = self.TELEPORT_COST
        self._level = 0

        self._found_boss = False

    def turn(self):
        if self.hp < self.max_hp:
            self._heal_clock += 1
            if self._heal_clock % self._heal_rate == 0:
                self.delta_hp += 1
                self._heal_clock = 0
        super().turn()

    def has_skill(self, skill: type(Skill)):
        return skill in self.__skills

    def level_up(self):
        for lvl, lvl_dict in self.__levels.items():
            if self._xp > lvl_dict['xp']:
                if lvl > self._level:
                    self._level = lvl
                    self.__skills.append(lvl_dict['skill'])
                    self.scene.log(f"You leveled up! You learned the spell {lvl_dict['skill'].NAME} "
                                   f"({lvl_dict['skill'].KEY})")
                    break

    @property
    def level(self):
        return self._level

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
    def freeze_damage(self):
        return self._freeze_damage + int(self.level / 3)

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
    def teleport_cost(self):
        return self._teleport_cost
