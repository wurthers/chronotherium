from enum import Enum
from typing import TYPE_CHECKING
from random import randrange

from bearlibterminal import terminal as bearlib

from chronotherium.entities.entity import EntityType, EnemyMode
from clubsandwich.blt.context import BearLibTerminalContext as Context
from clubsandwich.geom import Point
from clubsandwich.tilemap import CellOutOfBoundsError

from chronotherium.tiles.tile import Door, Stairs, StairsUp
from chronotherium.time import Time, TimeError
from chronotherium.window import Window, Color
from chronotherium.entities.player import Rewind, Freeze, Push, Diagonal, Teleport

if TYPE_CHECKING:
    from chronotherium.scene import GameScene
    from chronotherium.entities.player import Player


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

    RANGED = bearlib.TK_F
    REWIND = bearlib.TK_R
    PUSH = bearlib.TK_P
    DIAGONAL = bearlib.TK_E
    FREEZE = bearlib.TK_F
    WORMHOLE = bearlib.TK_W
    PICKUP = bearlib.TK_COMMA
    PICKUP_G = bearlib.TK_G
    LOOK = bearlib.TK_SEMICOLON
    OPEN = bearlib.TK_O
    TELEPORT = bearlib.TK_T


class ShiftCommand(Enum):
    STAIRS_UP = bearlib.TK_PERIOD
    STAIRS_DOWN = bearlib.TK_COMMA


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
            # Command.RANGED: self.ranged,
            Command.REWIND: self.rewind,
            # Command.HURT: self.hurt_player,
            # Command.DRAIN: self.drain_player,
            # Command.GAIN: self.gain_xp,
            Command.PUSH: self.push,
            Command.DIAGONAL: self.diagonal,
            Command.FREEZE: self.freeze,
            Command.PICKUP: self.pickup,
            Command.PICKUP_G: self.pickup,
            # Command.LOOK: self.look,
            Command.OPEN: self.open,
            Command.TELEPORT: self.teleport
        }

        self.__shift_command_map = {
            ShiftCommand.STAIRS_UP: self.stairs,
            ShiftCommand.STAIRS_DOWN: self.stairs
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
        if bearlib.check(bearlib.TK_SHIFT):
            try:
                return self.__shift_command_map[ShiftCommand(key)]()
            except ValueError:
                pass
        else:
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

    def ranged(self):
        pass

    def rewind(self):
        if not self.player.has_skill(Rewind):
            return
        state = None

        right_arrow = False
        left_arrow = True

        self.player.record()
        if self.player.tp < self.player.rewind_cost:
            self.scene.log(f"You don't have enough mana to rewind.")
            return False

        true_tick = self.time.time
        current_tick = self.time.time
        limit = current_tick - self.player.rewind_limit

        bearlib.color(Color.ORANGE)
        self.scene.print_stats(right_arrow=right_arrow, left_arrow=left_arrow)
        self.scene.draw_tiles()
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
                    self.scene.draw_tiles()
                    self.scene.draw_entities()
                    self.scene.print_log()
                    bearlib.refresh()

            key = bearlib.read()

        return False

    def freeze(self):
        if not self.player.has_skill(Freeze):
            return False

        if self.player.tp < self.player.freeze_cost:
            self.scene.log(f"You don't have enough mana to cast freeze.")
            return False

        target_square = self.scene.map.find_in_bounds_orthogonal(self.player.position)
        bearlib.bkcolor(Color.BLUE)
        self.scene.map.floor.cell(target_square).draw_tile(self.context)
        bearlib.bkcolor(self.window.bg_color)
        bearlib.refresh()

        key = bearlib.read()
        while key != bearlib.TK_ESCAPE:
            if key == bearlib.TK_ENTER or key == bearlib.TK_SPACE:
                target_tile = self.scene.map.floor.cell(target_square)
                enemy = None
                for entity in target_tile.entities:
                    if entity.type == EntityType.ENEMY:
                        enemy = entity
                        break
                if enemy is not None:
                    self.player.delta_tp -= self.player.freeze_cost
                    turns = randrange(1, 3)
                    # +1 -- Account for this current turn
                    enemy.freeze(turns + 2)
                    enemy.delta_hp -= self.player.freeze_damage
                    enemy.update_hp()
                    self.scene.log(f'You freeze the {enemy.name} in suspended animation. {enemy.hp}/{enemy.max_hp}')
                    return True
                else:
                    self.scene.log("There's nothing there to freeze.")
                    return False
            try:
                direction = Direction(key)
            except ValueError:
                key = bearlib.read()
                continue

            # Clears background from previous tile.
            target_tile = self.scene.map.floor.cell(target_square)
            bearlib.bkcolor(self.window.bg_color)
            target_tile.draw_tile(self.context)

            delta = self.__delta_map[direction]
            target_square = self.player.position + delta
            target_tile = self.scene.map.floor.cell(target_square)
            bearlib.bkcolor(Color.BLUE)
            target_tile.draw_tile(self.context)
            for entity in target_tile.entities:
                entity.draw(self.context)
            bearlib.bkcolor(self.window.bg_color)
            bearlib.refresh()

            key = bearlib.read()

    def push(self):
        if not self.player.has_skill(Push):
            return

        if self.player.tp < self.player.push_cost:
            self.scene.log(f"You don't have enough mana to open a wormhole.")
            return False

        target_square = self.scene.map.find_in_bounds_orthogonal(self.player.position, delta=2)
        self.context.bkcolor(Color.MAGENTA)
        target_tile = self.scene.map.floor.cell(target_square)
        target_tile.draw_tile(self.context)
        for entity in target_tile.entities:
            entity.draw(self.context)
        self.context.bkcolor(self.window.bg_color)
        bearlib.refresh()

        direction = Direction.WAIT

        key = bearlib.read()
        while key != bearlib.TK_ESCAPE:
            if key == bearlib.TK_ENTER or key == bearlib.TK_SPACE:
                try:
                    target_tile = self.scene.map.floor.cell(target_square)
                except CellOutOfBoundsError:
                    key = bearlib.read()
                    continue
                enemy = None
                for entity in target_tile.entities:
                    if entity.type == EntityType.ENEMY:
                        enemy = entity
                        break
                if enemy is not None:
                    self.player.delta_tp -= self.player.push_cost
                    self.player.update_tp()

                    delta = self.__delta_map[direction]
                    tile = self.scene.map.floor.cell(enemy.position + delta)

                    enemy.mode = EnemyMode.STUNNED
                    enemy.delta_hp -= self.player.push_damage

                    if tile.block:
                        enemy.delta_hp -= 1
                    else:
                        enemy.delta_pos += delta
                        enemy.update_pos()
                    enemy.update_hp()
                    self.scene.log(f'You rip open a wormhole and push the {enemy.name} through. '
                                   f'{enemy.hp}/{enemy.max_hp}')
                    return True
                else:
                    self.scene.log("There's nothing there to push.")
                    return False
            try:
                direction = Direction(key)
            except ValueError:
                key = bearlib.read()
                continue

            # Clears background from previous tile.
            bearlib.bkcolor(self.window.bg_color)
            target_tile.draw_tile(self.context)

            delta = self.__delta_map[direction] * 2
            target_square = self.player.position + delta
            try:
                target_tile = self.scene.map.floor.cell(target_square)
            except CellOutOfBoundsError:
                key = bearlib.read()
                continue
            self.context.bkcolor(Color.MAGENTA)
            target_tile.draw_tile(self.context)
            for entity in target_tile.entities:
                entity.draw(self.context)
            bearlib.bkcolor(self.window.bg_color)
            bearlib.refresh()

            key = bearlib.read()

    def diagonal(self):
        if not self.player.has_skill(Diagonal):
            return

        if self.player.tp < self.player.diagonal_cost:
            self.scene.log(f"You don't have enough mana to cast Event Horizon.")
            return False

        targets = self.scene.map.diagonals(self.player.position)
        bearlib.bkcolor(Color.YELLOW)
        for target in targets:
            target.draw_tile(self.context)
        bearlib.bkcolor(self.window.bg_color)
        bearlib.refresh()

        key = bearlib.read()
        while key != bearlib.TK_ESCAPE:
            if key == bearlib.TK_ENTER or key == bearlib.TK_SPACE:
                enemies = []
                for target in targets:
                    for entity in target.entities:
                        if entity.type == EntityType.ENEMY:
                            enemies.append(entity)
                        break
                self.player.delta_tp -= self.player.diagonal_cost
                self.player.update_tp()

                for enemy in enemies:
                    enemy.delta_hp -= self.player.diagonal_damage
                    enemy.update_hp()
                self.scene.log(f'You conjure a swarm of ephemeral black holes.')
                return True
            key = bearlib.read()

    def teleport(self):
        if not self.player.has_skill(Teleport):
            return

        if self.player.tp < self.player.teleport_cost:
            self.scene.log(f"You don't have enough mana to teleport.")
            return False

        self.player.delta_tp -= self.player.teleport_cost
        dest = self.scene.map.floor.find_open_point()
        self.player.delta_pos = dest - self.player.position
        return True

    def pickup(self):
        entities = self.player.tile.entities
        for entity in entities:
            if entity.type == EntityType.ITEM:
                entity.on_pickup()
        return False

    def look(self):
        pass

    def open(self):
        key = bearlib.read()

        while True:
            try:
                direction = Direction(key)
            except ValueError:
                key = bearlib.read()
                self.scene.log("Open what?")
                continue

            delta = self.__delta_map[direction]
            target_square = self.player.position + delta
            target_tile = self.scene.map.floor.cell(target_square)

            if not isinstance(target_tile, Door):
                self.scene.log("There's no door there.")
                return False
            else:
                if target_tile.interact():
                    if target_tile.door_open:
                        self.scene.log("The door remembers a time when it was open.")
                    else:
                        self.scene.log("The door thumps shut.")
                    target_tile.draw_tile(self.context)
                else:
                    self.scene.log("There's something blocking the doorway.")
                return True

    def stairs(self):
        target_tile = self.scene.map.floor.cell(self.player.position)
        if not isinstance(target_tile, Stairs):
            self.scene.log("There are no stairs there.")
            return False
        else:
            dest_tile = target_tile.interact()
            if dest_tile:
                self.scene.map.move_floors(dest_tile.floor)
                self.player._floor = dest_tile.floor
                self.player.clear_states()
                self.player.position = dest_tile.point
                self.scene.log(f"You {'ascend' if isinstance(target_tile, StairsUp) else 'descend'} the stairs.")
                return True
