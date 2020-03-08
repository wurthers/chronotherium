from abc import ABC
from logging import getLogger
from typing import Optional, Union, TYPE_CHECKING

from bearlibterminal import terminal as bearlib

from chronotherium.tiles.tile import Stairs, Tile, Door
from clubsandwich.geom import Point, Rect, Size
from clubsandwich.line_of_sight import get_visible_points
from clubsandwich.tilemap import CellOutOfBoundsError
from clubsandwich.blt.context import BearLibTerminalContext as Context

from enum import Enum

from chronotherium.window import Window, Color
from chronotherium.time import Time, TimeError
from chronotherium.rand import d6

if TYPE_CHECKING:
    from chronotherium.scene import GameScene
    from chronotherium.map import Map


class ActorState(Enum):
    ALIVE = 'alive'
    DEAD = 'dead'
    VICTORIOUS = 'victorious'


class EnemyMode(Enum):
    WANDER = 'wander'
    ATTACK = 'attack'


class EntityType(Enum):
    PLAYER = 0
    ENEMY = 1
    ITEM = 2


class ActorType(Enum):
    PLAYER = 0x0040     # @
    BEAST = 0x0043      # C
    GOLEM = 0x0038      # 8
    KNIGHT = 0x004B     # K
    SENTRY = 0x0073     # s


class ItemType(Enum):
    POTION = 0x0021     # !
    HOURGLASS = 0xE000  # ⌛


class Entity(ABC):

    time = Time()
    logger = getLogger()

    NAME: str = ""
    DESCRIPTION: str = ""
    TYPE: EntityType = None
    GLYPH: Union[ActorType, ItemType] = None
    COLOR: Optional[Color] = None
    BLOCKING: bool = True
    LAYER: int = 1

    def __init__(self, tile: Tile, map: 'Map', scene: 'GameScene'):
        self._pos = tile.point
        self._floor = tile.floor

        self.window = Window()
        self.map = map
        self.scene = scene
        self.layer = self.LAYER

        self.type = self.TYPE
        self._glyph = self.GLYPH
        self.color = self.COLOR if self.COLOR is not None else self.window.fg_color
        self.blocking = self.BLOCKING
        self.state = ActorState.ALIVE
        self.update_block()

    @property
    def glyph(self) -> chr:
        """
        Returns the glyph to use to draw this entity
        """
        return chr(self._glyph.value)

    @property
    def tile(self):
        """
        Returns the cell at this entitiy's current position
        """
        return self._floor.cell(self._pos)

    @property
    def position(self) -> Point:
        """
        Returns the absolute coordinates of this entity as a Point
        """
        return self._pos

    @position.setter
    def position(self, value):
        self._pos = value

    @property
    def relative_position(self) -> Point:
        """
        Returns the coordinates of this entitiy relative to the map as drawn.
        """
        return self.map.origin - self._pos

    def draw(self, context):
        if context.state(bearlib.TK_COLOR) == self.color:
            context.color(self.window.fg_color)
        else:
            context.color(self.color)
        context.layer(self.layer)
        bearlib.composition(bearlib.TK_OFF)
        context.put(self.position, self.glyph)
        context.layer(0)
        context.color(self.window.fg_color)

    def erase(self):
        bearlib.clear(self._pos.x, self._pos.y, 1, 1)

    def unblock(self):
        if self.blocking and self in self.tile.entities:
            self.tile.entities.remove(self)

    def update_block(self):
        if self not in self.tile.entities:
            self.tile.entities.append(self)


class Actor(Entity, ABC):

    BASE_HP = 0
    BASE_TP = 0
    LAYER = 2
    RANGE = 0

    class State:

        def __init__(self, actor):
            self.hp = actor.hp
            self.tp = actor.tp
            self.pos = actor.position

    def __init__(self, tile: Tile, map: 'Map', scene: 'GameScene'):
        super().__init__(tile, map, scene)
        self.name = self.NAME
        self.description = self.DESCRIPTION
        self._hp = self.BASE_HP
        self._max_hp = self.BASE_HP
        self._tp = self.BASE_TP
        self._max_tp = self.BASE_TP
        self._xp = 0
        self._bump_damage = 1
        self._range = self.RANGE

        self.frozen = 0
        self.state = ActorState.ALIVE

        # Ephemeral deltas
        self.delta_hp = 0
        self.delta_tp = 0
        self.delta_pos = Point(0, 0)
        self.delta_xp = 0

        self._states = {}
        self._visible_points = get_visible_points(self.position, self.map.get_allows_light, max_distance=self._range)


    def actor_move(self, delta: Point):
        try:
            target_point = self._pos + delta
            dest_cell = self._floor.cell(target_point)
            # Don't let enemies move onto stairs
            if self.type == EntityType.ENEMY and isinstance(dest_cell, Stairs):
                return True
            if dest_cell.block and dest_cell.occupied:
                for entity in dest_cell.entities:
                    if self.type == EntityType.PLAYER and entity.type == EntityType.ENEMY:
                        return self.bump(entity)
                    if self.type == EntityType.ENEMY and entity.type == EntityType.PLAYER:
                        self.bump(entity)
            elif dest_cell.block:
                if isinstance(dest_cell, Door):
                    dest_cell.interact()
                    return True
                return False
            else:
                self.delta_pos = delta
                self.unblock()
                return True
        except CellOutOfBoundsError:
            return False

    def visible_to(self, other: Entity) -> bool:
        return other.position in self._visible_points

    def in_sight(self, tile: Tile) -> bool:
        return tile in self.visible_tiles

    def in_range(self, other):
        range_rect = Rect(self.position - Point(self._range, self._range), Size(self._range * 2, self._range * 2))
        return range_rect.contains(other.position)

    @property
    def visible_tiles(self):
        return [self.map.floor.cell(point) for point in self._visible_points]

    @property
    def range(self):
        return self._range

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
    def xp(self):
        return self._xp

    @property
    def states(self):
        return self._states

    @property
    def bump_damage(self):
        return self._bump_damage

    def level_up(self):
        pass

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
        self.update_xp()
        if self.frozen > 0:
            self.frozen -= 1
            if self.frozen == 0:
                self.scene.log(f'The {self.name} thaws.')
            else:
                self.scene.log(f'The {self.name} is stuck in time.')
            return
        else:
            self.update_pos()
        if self.state == ActorState.DEAD:
            self.on_death()

    def update_hp(self):
        if self.delta_hp != 0:
            if self.hp + self.delta_hp >= 0:
                self._hp += self.delta_hp
            if self.hp == 0:
                self.state = ActorState.DEAD
        self.delta_hp = 0

    def update_tp(self):
        if self.delta_tp != 0:
            if self.tp + self.delta_tp >= 0:
                self._tp += self.delta_tp
            self.delta_tp = 0

    def update_pos(self):
        if self.delta_pos != Point(0, 0):
            self.unblock()
            self._pos += self.delta_pos
            bearlib.clear(self._pos.x, self._pos.y, 1, 1)
            self.update_block()
            self._visible_points = get_visible_points(self.position, self.map.get_allows_light, max_distance=self._range)
        self.delta_pos = Point(0, 0)

    def update_xp(self):
        self._xp += self.delta_xp
        self.delta_xp = 0
        self.level_up()

    def clear_states(self):
        self._states = {}

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
            if not self._floor.cell(state.pos).open:
                state.pos = self.tile.closest_open_point(state.pos)
                self.scene.log(f'You were displaced!')
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
        self.tile.draw_tile(context)

        context.color(self.color)
        context.layer(1)
        context.put(state.pos, self.glyph)
        context.layer(0)
        context.color(self.window.fg_color)

    def change_floors(self):
        pass

    def bump(self, target):
        if d6():
            target.delta_hp -= self.bump_damage
            player_message = f"You use your regular meat hands to pummel the {target.name}. " \
                             f"({target.hp + target.delta_hp}/{target.max_hp})"
            enemy_message = f"The {self.name} bashes into you."
        else:
            player_message = f"You swing a fist at the the {target.name} but miss."
            enemy_message = f"The {self.name} charges for you but you manage to dodge."
        self.scene.log(f'{player_message if self._glyph == ActorType.PLAYER else enemy_message}')
        target.update_hp()
        return True

    def freeze(self, turns):
        self.frozen += turns

    def on_death(self):
        raise NotImplementedError('on_death must be implemented by child class.')


class Enemy(Actor, ABC):

    TYPE = EntityType.ENEMY
    DROP = None
    XP = None

    def __init__(self, tile: Tile, map, scene):
        super().__init__(tile, map, scene)
        self._drop = self.DROP
        self._xp = self.XP
        self._mode = EnemyMode.WANDER
        self._floor.entities.append(self)

    @property
    def drop(self):
        return self._drop

    def ai_behavior(self):
        if self.in_range(self.scene.player) and self.visible_to(self.scene.player):
            self._mode = EnemyMode.ATTACK
        else:
            self._mode = EnemyMode.WANDER
        if self._mode == EnemyMode.ATTACK:
            all_neighbors = [neighbor for neighbor in self.position.neighbors]
            all_neighbors.extend([neighbor for neighbor in self.position.diagonal_neighbors])
            if self.scene.player.position in all_neighbors and self.in_range(self.scene.player):
                self.bump(self.scene.player)
            else:
                path_to_target = [point for point in self.position.points_bresenham_to(self.scene.player.position)]
                try:
                    dest = path_to_target[1]
                except IndexError:
                    self.turn()
                    return True

                if self.map.floor.cell(dest).open:
                    self.actor_move(dest - self.position)
                else:
                    try:
                        dest = self.scene.player.position.get_closest_point([neighbor for neighbor in all_neighbors
                                                                            if self.map.floor.cell(neighbor).open])
                        self.actor_move(dest - self.position)
                    except IndexError:
                        pass
        elif self._mode == EnemyMode.WANDER:
            dest = self.map.random_open_adjacent(self.position)
            self.actor_move(dest - self.position)

        self.turn()
        return True

    def drop_item(self):
        if self.drop is not None:
            if d6(limit=0, over=True):
                item = self.drop(self.tile, self.map, self.scene)
                item.update_block()

    def on_death(self):
        self.unblock()
        self._floor.entities.remove(self)
        self.drop_item()
        self.scene.player.delta_xp += self.xp
