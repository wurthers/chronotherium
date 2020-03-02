from typing import Optional

from bearlibterminal import terminal as bearlib

from clubsandwich.geom import Point
from clubsandwich.tilemap import CellOutOfBoundsError

from enum import Enum

from chronotherium.window import Window, Color
from chronotherium.map import Map


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


class Entity:
    def __init__(self, x: int, y: int, type: EntityType, map: Map, color: Color = None, blocking: bool = True):
        self._x = x
        self._y = y

        self.window = Window()
        self.type = type
        self.color = color if color is not None else self.window.fg_color
        self.blocking = blocking
        self.state: Optional[ActorState] = None
        self.map = map

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
        return self.map.floor.cell(self.position)

    @property
    def position(self) -> Point:
        """
        Returns the absolute coordinates of this entity as a Point
        """
        return Point(self._x, self._y)

    @property
    def relative_position(self) -> Point:
        """
        Returns the coordinates of this entitiy relative to the map as drawn.
        """
        return self.map.origin - Point(self._x, self._y)

    def wakeup(self, context):
        context.color(self.color)
        context.layer(1)
        context.put(Point(self._x, self._y), self.glyph)
        context.layer(0)
        context.color(self.window.fg_color)

    def unblock(self):
        if self.blocking:
            self.tile.block = False
        if self in self.tile.occupied_by and len(self.tile.occupied_by) == 1:
            self.tile.occupied = False
            self.tile.occupied_by.remove(self)

    def update_block(self):
        if self.blocking:
            self.tile.block = True
            if not isinstance(self, Actor):
                self.tile.block_sight = True
        self.tile.occupied = True
        self.tile.occupied_by.append(self)

    def move_to(self, point: Point):
        self.unblock()
        bearlib.clear(self._x, self._y, 1, 1)
        self._x = point.x
        self._y = point.y


class Actor(Entity):
    def __init__(self, x: int, y: int, type: EntityType, map: Map, blocking=True, color=None):
        self.ranged = False
        self.state = ActorState.ALIVE
        super().__init__(x, y, type, map, blocking=blocking, color=color)

    def actor_move(self, delta):
        try:
            target_point = self.position + delta
            dest_cell = self.map.floor.cell(target_point)
            if dest_cell.occupied:
                for e in dest_cell.occupied_by:
                    if isinstance(self, Player) and isinstance(e, Actor) and not isinstance(e, Player):
                        self.melee_attack(e)
                    if not isinstance(self, Player) and isinstance(e, Player) and not isinstance(e, Actor):
                        self.melee_attack(e)
        except CellOutOfBoundsError:
            return
        else:
            self.move_to(target_point)

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


class Player(Actor):
    def __init__(self, x: int, y: int, map: Map, color=None):
        super().__init__(x, y, EntityType.PLAYER, map, blocking=True, color=color)
        self._hp = 20
        self._tp = 10

    @property
    def hp(self) -> int:
        return self._hp

    @property
    def tp(self) -> int:
        return self._tp
