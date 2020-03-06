from enum import Enum
from typing import TYPE_CHECKING
from random import randrange

from bearlibterminal import terminal as bearlib

from chronotherium.entities.entity import EntityType
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.geom import Point

from chronotherium.time import Time, TimeError
from chronotherium.window import Window, Color

if TYPE_CHECKING:
    from chronotherium.scene import GameScene, Player


class Direction(Enum):
    NE = bearlib.TK_KP_9
    NW = bearlib.TK_KP_7
    SE = bearlib.TK_KP_3
    SW = bearlib.TK_KP_1
    N = bearlib.TK_KP_8
    S = bearlib.TK_KP_2
    W = bearlib.TK_KP_4
    E = bearlib.TK_KP_6
    WAIT = bearlib.TK_KP_5

    VIM_NE = bearlib.TK_U
    VIM_NW = bearlib.TK_Y
    VIM_SE = bearlib.TK_N
    VIM_SW = bearlib.TK_B
    VIM_N = bearlib.TK_K
    VIM_S = bearlib.TK_J
    VIM_W = bearlib.TK_H
    VIM_E = bearlib.TK_L
    VIM_WAIT = bearlib.TK_SPACE


class Command(Enum):
    # TODO: Remove these
    HURT = bearlib.TK_MINUS
    DRAIN = bearlib.TK_0
    GAIN = bearlib.TK_KP_PLUS

    REWIND = bearlib.TK_R
    PUSH = bearlib.TK_P
    DIAGONAL = bearlib.TK_E
    FREEZE = bearlib.TK_F
    WORMHOLE = bearlib.TK_W
    PICKUP = bearlib.TK_COMMA


class Input:

    def __init__(self, player: 'Player', context: Context, scene: 'GameScene'):
        """
        Class to handle player input
        """
        self.player = player
        self.context = context
        self.scene = scene
        self.window = Window()
        self.time = Time()

        self.__command_map = {
            Command.REWIND: self.rewind,
            Command.HURT: self.hurt_player,
            Command.DRAIN: self.drain_player,
            Command.GAIN: self.gain_xp,
            Command.PUSH: self.push,
            Command.DIAGONAL: self.diagonal,
            Command.FREEZE: self.freeze,
            Command.WORMHOLE: self.wormhole,
            Command.PICKUP: self.pickup
        }

    __delta_map = {
        Direction.VIM_N: Point(0, -1),
        Direction.VIM_S: Point(0, 1),
        Direction.VIM_W: Point(-1, 0),
        Direction.VIM_E: Point(1, 0),
        Direction.VIM_NE: Point(1, -1),
        Direction.VIM_NW: Point(-1, -1),
        Direction.VIM_SE: Point(1, 1),
        Direction.VIM_SW: Point(-1, 1),
        Direction.VIM_WAIT: Point(0, 0),
        Direction.N: Point(0, -1),
        Direction.S: Point(0, 1),
        Direction.W: Point(-1, 0),
        Direction.E: Point(1, 0),
        Direction.NE: Point(1, -1),
        Direction.NW: Point(-1, -1),
        Direction.SE: Point(1, 1),
        Direction.SW: Point(-1, 1),
        Direction.WAIT: Point(0, 0)
    }

    def handle_key(self, key):
        try:
            return self.handle_move(Direction(key))
        except ValueError:
            pass
        try:
            return self.__command_map[Command(key)]()
        except ValueError:
            pass

    def handle_move(self, direction):
        return self.player.actor_move(self.__delta_map[direction])

    def handle_cursor(self, direction):
        return self.__delta_map[direction]

    def hurt_player(self):
        self.player.delta_hp -= 1
        self.player.record()
        self.player.turn()
        return True

    def drain_player(self):
        self.player.delta_tp -= 1
        self.player.record()
        self.player.turn()
        return True

    def gain_xp(self):
        self.player.delta_xp += 1
        self.player.record()
        self.player.turn()
        return False

    def rewind(self):
        state = None

        right_arrow = False
        left_arrow = True

        self.player.record()
        if self.player.tp < self.player.rewind_cost:
            self.scene.log(f'Not enough tp to rewind (costs {self.player.rewind_cost} TP)')
            return False

        true_tick = self.time.time
        current_tick = self.time.time
        limit = current_tick - self.player.rewind_limit

        bearlib.color(Color.ORANGE)
        self.scene.print_stats(right_arrow=right_arrow, left_arrow=left_arrow)
        self.scene.print_entities()
        bearlib.refresh()

        key = bearlib.read()
        while key != bearlib.TK_ESCAPE:
            if key == bearlib.TK_ENTER or key == bearlib.TK_SPACE:
                if state is not None:
                    # Only roll back if we are on a different tick than what we started at
                    if current_tick != true_tick:
                        self.player.delta_tp -= self.player.rewind_cost
                        self.time.restore(current_tick)
                        self.player.unblock()
                        self.player.restore_state(current_tick, hp=True, tp=False, pos=True)
                        self.player.turn()
                        self.player.update_block()
                return False
            try:
                direction = Direction(key)
            except ValueError:
                key = bearlib.read()
                continue
            if direction in (Direction.W, Direction.VIM_W, Direction.E, Direction.VIM_E):
                if direction in (Direction.W, Direction.VIM_W):
                    if (current_tick - 1) < limit:
                        key = bearlib.read()
                        continue
                    try:
                        state = self.player.preview_state(current_tick - 1)
                    except TimeError:
                        key = bearlib.read()
                        continue
                    current_tick -= 1
                elif direction in (Direction.E, Direction.VIM_E):
                    if (current_tick + 1) > self.time.time:
                        key = bearlib.read()
                        continue
                    try:
                        state = self.player.preview_state(current_tick + 1)
                    except TimeError:
                        key = bearlib.read()
                        continue
                    current_tick += 1

                if state is not None:
                    if current_tick == limit:
                        left_arrow = False
                        right_arrow = True
                    elif current_tick == true_tick:
                        right_arrow = False
                        left_arrow = True
                    else:
                        right_arrow = True
                        left_arrow = True

                    self.player.draw_preview(self.context, current_tick)
                    bearlib.color(Color.ORANGE)
                    self.scene.print_stats(hp=state.hp, tick=current_tick, right_arrow=right_arrow,
                                           left_arrow=left_arrow)

                    bearlib.color(self.window.fg_color)
                    self.scene.print_entities()
                    self.scene.print_log()
                    bearlib.refresh()

            key = bearlib.read()

        return False

    def freeze(self):

        target_square = self.player.position + Point(0, 1)
        bearlib.bkcolor(Color.BLUE)
        self.scene.map.floor.cell(target_square).draw_tile(self.context)
        bearlib.refresh()

        key = bearlib.read()
        while key != bearlib.TK_ESCAPE:
            if key == bearlib.TK_ENTER or key == bearlib.TK_SPACE:
                target_tile = self.scene.map.floor.cell(target_square)
                if not target_tile.occupied:
                    return False
                else:
                    enemy = None
                    for entity in target_tile.occupied_by:
                        if entity.type == EntityType.ENEMY:
                            enemy - entity
                            break
                    if enemy is not None:
                        self.player.delta_tp -= self.player.freeze_cost
                        turns = randrange(1, 2)
                        enemy.freeze(turns)
                        return True
                    else:
                        return False
            try:
                direction = Direction(key)
            except ValueError:
                key = bearlib.read()
                continue

            delta = self.__delta_map[direction]
            target_square = self.player.position + delta
            bearlib.bkcolor(Color.BLUE)
            self.scene.map.floor.cell(target_square).draw_tile(self.context)
            bearlib.refresh()

            bearlib.read()


    def push(self):
        pass

    def diagonal(self):
        pass

    def wormhole(self):
        pass

    def pickup(self):
        entities = self.player.tile.occupied_by
        for entity in entities:
            if entity.type == EntityType.ITEM:
                entity.on_pickup()
        return False
