from typing import TYPE_CHECKING
from abc import ABC

from chronotherium.tiles.tile import Tile
from chronotherium.entities.entity import Actor, EntityType, ActorType

if TYPE_CHECKING:
    from chronotherium.scene import GameScene
    from chronotherium.map import Map


class Skill(ABC):
    LEVEL = 0
    NAME = ''
    KEY = None
    COST = 0
    DAMAGE = 0
    LIMIT = 0
    DESCRIPTION = ''


class Freeze(Skill):
    LEVEL = 0
    NAME = 'Freeze'
    KEY = 'f'
    COST = 1
    DAMAGE = 1
    DESCRIPTION = 'Suspend your enemy in time'


class Teleport(Skill):
    LEVEL = 1
    NAME = 'Teleport'
    KEY = 't'
    COST = 2
    DESCRIPTION = 'Jump to a new where'


class Rewind(Skill):
    LEVEL = 2
    NAME = 'Rewind'
    KEY = 'r'
    COST = 3
    LIMIT = 3
    DESCRIPTION = 'Return to a previous when'


class Push(Skill):
    LEVEL = 3
    NAME = 'Wormhole'
    KEY = 'p'
    DAMAGE = 2
    COST = 2
    DESCRIPTION = 'Pushes and damages'


class Diagonal(Skill):
    LEVEL = 4
    NAME = 'Event Horizon'
    KEY = 'e'
    COST = 4
    DAMAGE = 3
    DESCRIPTION = 'Devastate multiple enemies'


class Player(Actor):

    __levels = {
        1: {'xp': 8, 'skill': Teleport},
        2: {'xp': 20, 'skill': Push},
        3: {'xp': 32, 'skill': Rewind},
        4: {'xp': 45, 'skill': Diagonal}
    }

    _skills = [Freeze]

    NAME = "Player"
    TYPE = EntityType.PLAYER
    GLYPH = ActorType.PLAYER
    RANGE = 8
    BASE_HP = 10
    BASE_TP = 6
    REWIND_LIMIT = 3
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
        self._rewind_limit = Rewind.LIMIT
        self._rewind_cost = Rewind.COST
        self._freeze_cost = Freeze.COST
        self._freeze_damage = Freeze.DAMAGE
        self._push_cost = Push.COST
        self._push_damage = Push.DAMAGE
        self._diagonal_cost = Diagonal.COST
        self._diagonal_damage = Diagonal.DAMAGE
        self._teleport_cost = Teleport.COST

        self._heal_rate = self.HEAL_RATE
        self._heal_clock = 0

        self._level = 0

        self._found_boss = False

    def turn(self):
        if self.hp < self.max_hp:
            self._heal_clock += 1
            if self._heal_clock % self._heal_rate == 0:
                self.delta_hp += 1
                self.delta_tp += 1
                self._heal_clock = 0
        super().turn()

    def has_skill(self, skill: type(Skill)):
        return skill in self._skills

    def level_up(self):
        for lvl, lvl_dict in self.__levels.items():
            if self._xp > lvl_dict['xp']:
                if lvl > self._level:
                    self._level = lvl
                    self._skills.append(lvl_dict['skill'])
                    self.scene.update_skills()
                    self.scene.log(f"You learned the spell {lvl_dict['skill'].NAME} "
                                   f"({lvl_dict['skill'].KEY})")
                    break

    def on_death(self):
        pass

    @property
    def skills(self):
        return self._skills

    @property
    def level(self):
        return self._level

    @property
    def max_hp(self):
        return self._max_hp + self.level * 3

    @property
    def max_tp(self):
        return self._max_tp + self.level

    @property
    def rewind_limit(self):
        return self._rewind_limit + self.level

    @property
    def rewind_cost(self):
        return self._rewind_cost

    @property
    def freeze_cost(self):
        return self._freeze_cost

    @property
    def freeze_damage(self):
        return self._freeze_damage + int(self.level / 4)

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
