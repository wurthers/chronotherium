from typing import List, Optional

from bearlibterminal import terminal as bearlib

from clubsandwich.geom import Rect, Point, Size
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.director import Scene

from chronotherium.window import Window, Color, LOG_HEIGHT, MAP_SIZE, MAP_ORIGIN
from chronotherium.map import Map
from chronotherium.entities.entity import Actor, ActorState, EntityType
from chronotherium.input import Input
from chronotherium.time import Time


class PrintScene(Scene):

    def __init__(self):
        self.window = Window()
        self.message_log = []
        self.gutter = []
        self.gutter_size = Size(self.window.width - MAP_SIZE.width + MAP_ORIGIN.x,
                                self.window.height - MAP_ORIGIN.y)
        self.gutter_rect = Rect(Point(self.window.width - self.gutter_size.width,
                                      self.window.height - self.gutter_size.height),
                                self.gutter_size)
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
        self.director.push_scene(FlavorScene())


class FlavorScene(PrintScene):

    def __init__(self):

        self.__input_map = {
            bearlib.TK_SPACE: self.next_scene,
            bearlib.TK_Q: self.quit,
            bearlib.TK_ESCAPE: self.quit
        }

        super().__init__()

    def terminal_update(self, is_active: bool = False):
        self.pprint_center(["You return to the palace in a new when,",
                            "but it feels feels all too familiar.", "",
                            "The beast has thwarted you once again,",
                            "as it has done so many times before.",
                            "How long have you pursued",
                            "it through these halls?", "",
                            "How many countless seconds,",
                            "subdividing eternity?", "",
                            "(Press Space to Continue)"])

    def terminal_read(self, val):
        try:
            self.__input_map[val]()
        except KeyError:
            pass

    def next_scene(self):
        self.director.push_scene(GameScene())

    def quit(self):
        self.director.pop_scene()


class GameScene(PrintScene):

    time = Time()

    def __init__(self):
        super().__init__()

        self.pprint_center(["Generating..."])

        self.__input_map = {
            bearlib.TK_Q: self.quit,
            bearlib.TK_ESCAPE: self.quit
        }

        self.context = Context()
        try:
            self.map = Map(self)
        except Exception as err:
            # This is here for debugging purposes
            pass

        self.player = self.map.player
        self.input = Input(self.player, self.context, self)
        self.update_skills()

    @property
    def entities(self):
        return self.map.floor.entities

    @property
    def relative_pos(self) -> Point:
        return self.player.relative_position + self.map.view_center

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

    def draw_tiles(self):
        for cell in self.map.floor.cells:
            if self.bounds.contains(cell.point + self.relative_pos):
                if not cell.occupied and self.player.in_sight(cell):
                    cell.draw_tile(self.context)

    def draw_entities(self):
        for entity in self.entities:
            if self.player.visible_to(entity):
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
        tp_string = f'MP: {"|" * tp}{" " * (self.player.max_tp - self.player.tp)} '\
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

    def update_skills(self):
        skill_strings = []
        for skill in self.player.skills:
            skill_string = f"{skill.NAME} ({skill.COST} MP): {skill.KEY}"
            skill_desc = f"{skill.DESCRIPTION}"
            skill_strings.extend([skill_string, skill_desc, ""])

        self.gutter = skill_strings

    def print_gutter(self, strings: Optional[List[str]] = None):
        if strings is None:
            strings = self.gutter
        for i in range(0, len(strings)):
            string = strings[i]
            self.pprint(self.gutter_rect.x, self.gutter_rect.y + i, string)

    def terminal_read(self, val) -> None:
        if val in self.__input_map:
            self.__input_map[val]()
        with self.context.translate(self.relative_pos):
            if self.input.handle_key(val):
                self.player.turn()
                for entity in self.entities:
                    if self.bounds.contains(entity.position + self.relative_pos):
                        if entity.type == EntityType.ENEMY:
                            entity.ai_behavior()
                self.time.tick()

    def terminal_update(self, is_active: bool = False) -> None:
        if self.player.state == ActorState.DEAD:
            self.director.replace_scene(DeathScene())
        elif self.player.state == ActorState.VICTORIOUS:
            self.director.replace_scene(VictoryScene())
        bearlib.clear()
        with self.context.translate(self.relative_pos):
            self.draw_tiles()
            for entity in self.entities:
                if isinstance(entity, Actor):
                    if entity.state == ActorState.DEAD:
                        self.entities.remove(entity)
                        continue
                if self.bounds.contains(entity.position + self.relative_pos):
                    if self.player.visible_to(entity):
                        entity.draw(self.context)
            self.player.draw(self.context)
            self.print_stats()
            self.print_log()
            self.print_gutter()
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
