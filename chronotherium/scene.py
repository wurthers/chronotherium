from typing import List

from bearlibterminal import terminal as bearlib

from clubsandwich.geom import Rect, Point
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.director import Scene

from chronotherium.window import Window, Color, LOG_HEIGHT, MAP_SIZE, VIEW_SIZE, MAP_ORIGIN
from chronotherium.map import Map
from chronotherium.entities.entity import Actor, ActorState, EntityType
from chronotherium.entities.player import Player
from chronotherium.entities.chronotherium import Chronotherium
from chronotherium.input import Input
from chronotherium.time import Time


class PrintScene(Scene):

    def __init__(self):
        self.window = Window()
        self.message_log = []
        self.gutter = []
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
        bearlib.composition(bearlib.TK_ON)
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
        bearlib.composition(bearlib.TK_OFF)

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
        self.entities = []

        self.__input_map = {
            bearlib.TK_Q: self.quit,
            bearlib.TK_ESCAPE: self.quit
        }

        self.map = Map(MAP_SIZE, VIEW_SIZE, MAP_ORIGIN, self)

        self.map.populate_floor({Chronotherium: 1})
        self.context = Context()
        self.player = Player(self.map.view_center, self.map, self)
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

    def print_tiles(self):
        for cell in self.map.floor.cells:
            if self.bounds.contains(cell.point + self.relative_pos):
                if not cell.occupied:
                    cell.draw_tile(self.context)

    def print_entities(self):
        for entity in self.entities:
            entity.draw(self.context)

    def print_stats(self, hp: int = None, tp: int = None, tick: int = None, left_arrow: bool = False,
                    right_arrow: bool = False):

        color = bearlib.state(bearlib.TK_COLOR)
        corner = self.map.view_rect.point_bottom_left
        bearlib.clear_area(corner.x, corner.y + 1, self.window.width, self.window.height - corner.y + 1)

        if hp is None:
            hp = self.player.hp
        if tp is None:
            tp = self.player.tp
        hp_string = f'HP: {"|" * hp}{" " * (self.player.max_hp - self.player.hp)} '\
                    f'({self.player.hp}/{self.player.max_hp})'
        tp_string = f'TP: {"|" * tp}{" " * (self.player.max_tp - self.player.tp)} '\
                    f'({self.player.tp}/{self.player.max_tp})'
        xp_string = f'XP: {self.player.xp} - Level {self.player.level}'
        time_string = f'{"<" if left_arrow else " "}Time: {self.time.clock(tick)}{">" if right_arrow else ""}'
        bearlib.color(Color.RED)
        self.pprint(corner.x, corner.y + 1, hp_string)
        bearlib.color(Color.VIOLET)
        self.pprint(corner.x, corner.y + 2, tp_string)
        bearlib.color(Color.YELLOW)
        self.pprint(corner.x, corner.y + 3, xp_string)
        bearlib.color(color)
        self.pprint(corner.x, corner.y + 4, time_string)
        bearlib.color(self.window.fg_color)

    def terminal_read(self, val) -> None:
        if val in self.__input_map:
            self.__input_map[val]()
        with self.context.translate(self.relative_pos):
            if self.input.handle_key(val):
                self.player.turn()
                for entity in self.entities:
                    if entity.type == EntityType.ENEMY and entity.ai_behavior():
                        entity.turn()
                self.time.tick()

    def terminal_update(self, is_active: bool = False) -> None:
        if self.player.state == ActorState.DEAD:
            self.director.replace_scene(DeathScene())
        elif self.player.state == ActorState.VICTORIOUS:
            self.director.replace_scene(VictoryScene())
        bearlib.clear()
        with self.context.translate(self.relative_pos):
            self.print_tiles()
            for entity in self.entities:
                if isinstance(entity, Actor):
                    if entity.state == ActorState.DEAD:
                        self.entities.remove(entity)
                        continue
                if self.bounds.contains(entity.position + self.relative_pos):
                    entity.draw(self.context)
            self.player.draw(self.context)
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
