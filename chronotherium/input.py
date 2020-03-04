from enum import Enum
from typing import TYPE_CHECKING

from bearlibterminal import terminal as bearlib
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.geom import Point

from chronotherium.time import Time, TimeError
from chronotherium.entities.player import Player
from chronotherium.window import Window, Color

if TYPE_CHECKING:
    from chronotherium.scene import GameScene


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
    REWIND = bearlib.TK_R
    HURT = bearlib.TK_MINUS


class Input:

    def __init__(self, player: Player, context: Context, scene: 'GameScene'):
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
            Command.HURT: self.hurt_player
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
        self.player.delta_hp = -1
        return True

    def rewind(self):

        current_tick = self.time.time
        limit = current_tick - self.player.rewind_limit

        key = bearlib.read()
        state = None
        while key != bearlib.TK_ESCAPE:
            bearlib.color(Color.ORANGE)
            try:
                direction = Direction(key)
            except ValueError:
                continue
            if direction in (Direction.W, Direction.VIM_W, Direction.E, Direction.VIM_E):
                if direction in (Direction.W, Direction.VIM_W):
                    if (current_tick - 1) < limit:
                        continue
                    try:
                        state = self.player.preview_state(current_tick - 1)
                    except TimeError:
                        continue
                    current_tick -= 1
                elif direction in (Direction.E, Direction.VIM_E):
                    try:
                        state = self.player.preview_state(current_tick + 1)
                    except TimeError:
                        continue
                    current_tick += 1

                if state is not None:
                    self.player.draw_preview(self.context, current_tick)
                    self.scene.print_time(right_arrow=True, left_arrow=True)

                    bearlib.color(self.window.fg_color)
                    for cell in self.scene.map.floor.cells:
                        if self.scene.bounds.contains(cell.point + self.scene.relative_pos):
                            if not cell.occupied:
                                cell.draw_tile(self.context)
                    self.scene.print_stats()
                    self.scene.print_log()
                    bearlib.refresh()

            elif key == bearlib.TK_ENTER:
                if state is not None:
                    self.time.restore(current_tick)
                    self.player.restore_state(current_tick, hp=True, tp=False, pos=True)
                return False

            key = bearlib.read()

        return False
