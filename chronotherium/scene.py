from typing import List

from bearlibterminal import terminal as bearlib

from clubsandwich.geom import Rect, Point
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.director import Scene

from chronotherium.window import Window, Color, LOG_HEIGHT, MAP_SIZE, VIEW_SIZE, MAP_ORIGIN
from chronotherium.map import Map
from chronotherium.entities.entity import Actor, ActorState
from chronotherium.entities.player import Player
from chronotherium.entities.chronotherium import Chronotherium
from chronotherium.input import Input
from chronotherium.time import Time


class PrintScene(Scene):

    def __init__(self):
        self.window = Window()
        self.message_log = []
        self.log_height = LOG_HEIGHT
        super().__init__()

    def pprint(self, x: int, y: int, string: str):
        """
        Pretty prints a string starting at (x,y).
        :param x: x coordinate

        :param y: y coordinate

        :param string: String to print to screen
        """
        bearlib.layer(1)
        bearlib.composition("TK_ON")
        pos = x
        cell_size, _ = self.window.cell_size.split('x')
        cell_width = int(cell_size)
        for c in string:
            if pos >= self.window.width - x - 1:
                pos = pos + 1
                offset = (pos - x) * (cell_width / 2)
                bearlib.put_ext(x, y, int(offset), 0, c)
            else:
                pos = pos + 1
                offset = 0 - pos * (cell_width / 2)
                bearlib.put_ext(pos, y, int(offset), 0, c)
        bearlib.layer(0)
        bearlib.composition("TK_OFF")

    def pprint_center(self, text: List[str]):
        """
        Prints a string or list of strings in the center of the window

        :param text: List of strings to be printed
        """
        height = self.window.height
        width = self.window.width
        cellsize, _ = self.window.cell_size.split('x')
        cell_width = int(cellsize)
        center = int(width / 2)

        bearlib.clear()
        bearlib.layer(1)
        bearlib.composition("TK_ON")
        y = int(height / 2 - len(text) / 2)
        for i, s in enumerate(text):
            middle_char = int(len(s) / 2)
            x = int(center - middle_char)
            pos = 0
            for c in s:
                offset = (center - x) * (cell_width / 2)
                bearlib.put_ext(x, y + i, int(offset), 0, c)
                x = x + 1
                pos = pos + 1
        bearlib.composition("TK_OFF")
        bearlib.layer(0)
        bearlib.refresh()

    def log(self, msg):
        cutoff = self.window.width - 3
        while len(msg) > cutoff * 2:
            sub_msg, trailing = msg[:cutoff * 2].rsplit(' ', 1)
            self.message_log.append(sub_msg)
            msg = trailing + msg[cutoff * 2:]
        self.message_log.append(msg)

    def print_log(self):
        for i, msg in enumerate(self.message_log[-self.log_height:]):
            self.pprint(0, i, msg)


class StartScene(PrintScene):

    def __init__(self):

        self.__input_map = {
            bearlib.TK_SPACE: self.next_scene,
            bearlib.TK_Q: self.quit,
            bearlib.TK_ESCAPE: self.quit
        }

        super().__init__()

    def terminal_update(self, is_active: bool = False):
        self.pprint_center(["Chronotherium", "A 2020 7DRL", "by wurthers", "", "Space - Start", "Esc, Q - Quit"])

    def terminal_read(self, val):
        try:
            self.__input_map[val]()
        except KeyError:
            pass

    def quit(self):
        self.director.pop_scene()

    def next_scene(self):
        self.director.push_scene(GameScene())


class GameScene(PrintScene):

    time = Time()

    def __init__(self):
        super().__init__()

        self.__input_map = {
            bearlib.TK_Q: self.quit,
            bearlib.TK_ESCAPE: self.quit
        }

        self.map = Map(MAP_SIZE, VIEW_SIZE, MAP_ORIGIN)

        self.entities = self.map.populate_floor({Chronotherium: 1})
        self.context = Context()
        self.player = Player(self.map.view_center, self.map)
        self.input = Input(self.player, self.context, self)

    @property
    def relative_pos(self) -> Point:
        return self.player.relative_position + self.map.center

    @property
    def bounds(self) -> Rect:
        return Rect(self.map.origin, self.map.view_size)

    def quit(self):
        self.context.clear()
        self.pprint_center(["Are you sure you", "want to quit?", "", "Space - Yes ", "Esc - No"])
        self.context.refresh()
        while True:
            key = bearlib.read()
            if key == bearlib.TK_SPACE:
                self.director.quit()
                break
            elif key == bearlib.TK_ESCAPE:
                break

    def print_time(self, tick: int = None, left_arrow: bool = False, right_arrow: bool = False):
        corner = self.map.view_rect.point_bottom_right
        display = f'{"<" if left_arrow else " "}Time: {self.time.clock(tick)}{">" if right_arrow else " "}'
        self.pprint(corner.x - int(len(display) / 2), corner.y + 1, display)

    def print_stats(self, hp: int = None, tp: int = None):
        corner = self.map.view_rect.origin
        hp_string = f'HP: {"|" * self.player.hp if hp is None else "|" * hp}'\
                    f'{" " * (self.player.max_hp - self.player.hp)} ({self.player.hp}/{self.player.max_hp})'
        tp_string = f'TP: {"|" * self.player.tp if tp is None else "|" * tp}'\
                    f'{" " * (self.player.max_tp - self.player.tp)} ({self.player.tp}/{self.player.max_tp})'
        bearlib.color(Color.RED)
        self.pprint(corner.x, corner.y - 2, hp_string)
        bearlib.color(Color.VIOLET)
        self.pprint(corner.x, corner.y - 1, tp_string)
        bearlib.color(self.window.fg_color)

    def terminal_read(self, val) -> None:
        if val in self.__input_map:
            self.__input_map[val]()
        with self.context.translate(self.relative_pos):
            if self.input.handle_key(val):
                self.time.tick()

    def terminal_update(self, is_active: bool = False) -> None:
        if self.player.state == ActorState.DEAD:
            self.director.replace_scene(DeathScene())
        elif self.player.state == ActorState.VICTORIOUS:
            self.director.replace_scene(VictoryScene())
        bearlib.clear()
        with self.context.translate(self.relative_pos):
            for cell in self.map.floor.cells:
                if self.bounds.contains(cell.point + self.relative_pos):
                    if not cell.occupied:
                        cell.draw_tile(self.context)
            for entity in self.entities:
                if isinstance(entity, Actor):
                    if entity.state == ActorState.DEAD:
                        self.entities.remove(entity)
                        entity.on_death()
                        continue
                if self.bounds.contains(entity.position + self.relative_pos):
                    entity.draw(self.context)
            self.player.draw(self.context)
            self.print_time(right_arrow=True, left_arrow=True)
            self.print_stats()
            self.print_log()
            bearlib.refresh()


class DeathScene(PrintScene):
    def terminal_update(self, is_active=False):
        self.pprint_center(["You died, lost to the winds of time.", "R - Restart", "Q, ESC - Quit"])

    def terminal_read(self, val):
        if val == bearlib.TK_R:
            self.director.replace_scene(GameScene())
        elif val == bearlib.TK_ESCAPE or val == bearlib.TK_Q:
            self.director.quit()


class VictoryScene(PrintScene):
    def terminal_update(self, is_active=False):
        self.pprint_center(["You have slain the time beast!", "The golden hourglass is yours!!!",
                            "R - Restart", "Q, ESC - Quit"])

    def terminal_read(self, val):
        if val == bearlib.TK_R:
            self.director.replace_scene(GameScene())
        elif val == bearlib.TK_ESCAPE or val == bearlib.TK_Q:
            self.director.quit()
