from abc import ABC
from logging import getLogger
from typing import Optional

from bearlibterminal import terminal as bearlib

from clubsandwich.geom import Point
from clubsandwich.tilemap import CellOutOfBoundsError
from clubsandwich.blt.context import BearLibTerminalContext as Context

from enum import Enum

from chronotherium.window import Window, Color
from chronotherium.map import Map
from chronotherium.time import Time, TimeError


class ActorState(Enum):
    ALIVE = 'alive'
    DEAD = 'dead'


class EnemyMode(Enum):
    WANDER = 'wander'
    ATTACK = 'attack'
    STUNNED = 'stunned'


class EntityType(Enum):
    PLAYER = 0x0040     # @
    ENEMY = 0x003F      # ?
    BEAST = 0x0043      # C


class Entity(ABC):

    time = Time()
    logger = getLogger()

    NAME: str = ""
    DESCRIPTION: str = ""
    TYPE: EntityType = None
    COLOR: Optional[Color] = None
    BLOCKING: bool = True

    def __init__(self, position: Point, map: Map):
        self._pos = position

        self.window = Window()
        self.map = map

        self.type = self.TYPE
        self.color = self.COLOR if self.COLOR is not None else self.window.fg_color
        self.blocking = self.BLOCKING
        self.state = ActorState.ALIVE

    @property
    def glyph(self) -> chr:
        """
        Returns the glyph to use to draw this entity
        """
        return chr(self.type.value)

    @property
    def tile(self):
        """
        Returns the cell at this entitiy's current position
        """
        return self.map.floor.cell(self._pos)

    @property
    def position(self) -> Point:
        """
        Returns the absolute coordinates of this entity as a Point
        """
        return self._pos

    @property
    def relative_position(self) -> Point:
        """
        Returns the coordinates of this entitiy relative to the map as drawn.
        """
        return self.map.origin - self._pos

    def draw(self, context):
        context.color(self.color)
        context.layer(1)
        context.put(self.position, self.glyph)
        context.layer(0)
        context.color(self.window.fg_color)

    def erase(self):
        bearlib.clear(self._pos.x, self._pos.y, 1, 1)

    def unblock(self):
        if self.blocking:
            self.tile.block = False
        if self in self.tile.occupied_by:
            if len(self.tile.occupied_by) == 1:
                self.tile.occupied = False
            self.tile.occupied_by.remove(self)

    def update_block(self):
        if self.blocking:
            self.tile.block = True
            if not isinstance(self, Actor):
                self.tile.block_sight = True
        self.tile.occupied = True
        self.tile.occupied_by.append(self)


class Actor(Entity, ABC):

    BASE_HP = 0
    BASE_TP = 0

    class State:

        def __init__(self, actor):
            self.hp = actor.hp
            self.tp = actor.tp
            self.pos = actor.position

    def __init__(self, position: Point, map: Map):
        self.name = self.NAME
        self.description = self.DESCRIPTION
        self._hp = self.BASE_HP
        self._max_hp = self.BASE_HP
        self._tp = self.BASE_TP
        self._max_tp = self.BASE_TP

        self.state = ActorState.ALIVE

        # Ephemeral deltas
        self.delta_hp = 0
        self.delta_tp = 0
        self.delta_pos = Point(0, 0)

        self._states = {}

        super().__init__(position, map)

    def actor_move(self, delta: Point):
        try:
            target_point = self._pos + delta
            dest_cell = self.map.floor.cell(target_point)
            if dest_cell.occupied:
                for e in dest_cell.occupied_by:
                    if self.type == EntityType.PLAYER and e.type == EntityType.ENEMY:
                        self.melee_attack(e)
                    if self.type == EntityType.ENEMY and e.type == EntityType.PLAYER:
                        self.melee_attack(e)
            if dest_cell.block:
                return False
        except CellOutOfBoundsError:
            return False
        else:
            self.delta_pos = delta
            self.turn()
            return True

    @property
    def max_hp(self):
        return self._max_hp

    @property
    def max_tp(self):
        return self._max_tp

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def tp(self) -> int:
        return self._tp

    @property
    def states(self):
        return self._states

    def record(self):
        tick = self.time.time
        self._states[tick] = self.State(self)

    def turn(self):
        self.record()
        tick = self.time.time
        if self._states.get(tick - self.time.MAX_RECORD):
            del self._states[tick - self.time.MAX_RECORD]
        self.update_hp()
        self.update_tp()
        self.update_pos()

    def update_hp(self):
        if self.delta_hp != 0:
            self._hp += self.delta_hp
            self.delta_hp = 0

    def update_tp(self):
        if self.delta_tp != 0:
            self._tp += self.delta_tp
            self.delta_tp = 0

    def update_pos(self):
        if self.delta_pos != Point(0, 0):
            self._pos += self.delta_pos
            bearlib.clear(self._pos.x, self._pos.y, 1, 1)
            self.unblock()
        self.delta_pos = Point(0, 0)

    def restore_state(self, tick: int, hp=True, tp=True, pos=True) -> None:
        """
        Restores state of this entity at the given turn
        """
        try:
            state = self._states[tick]
        except KeyError:
            raise TimeError("No state recorded for tick {}".format(tick)) from None
        if hp:
            self._hp = state.hp
        if tp:
            self._tp = state.tp
        if pos:
            self._pos = state.pos

    def preview_state(self, tick: int):
        """
        Return this entity's state for the given turn without modifying it
        """
        try:
            state = self._states[tick]
        except KeyError:
            raise TimeError("No state recorded for tick {}".format(tick)) from None

        return state

    def draw_preview(self, context: Context, time: int):
        state = self.preview_state(time)
        self.erase()

        context.color(self.color)
        context.layer(1)
        context.put(state.pos, self.glyph)
        context.layer(0)
        context.color(self.window.fg_color)

    # def change_floors(self):
    #     pass

    # def suffer(self):
    #     pass

    # def ai_behavior(self, player):
    #     pass

    def melee_attack(self, target):
        pass

    # def ranged_attack(self, target_cell):
    #     pass

    def on_death(self):
        pass
