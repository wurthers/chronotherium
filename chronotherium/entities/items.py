from abc import ABC

from chronotherium.entities.entity import Entity, EntityType, ItemType, ActorState
from chronotherium.window import Color


class Item(Entity, ABC):

    TYPE = EntityType.ITEM
    BLOCKING = False

    def __init__(self, position, map, scene):
        super().__init__(position, map, scene)
        self.scene.entities.append(self)

    def on_pickup(self):
        self.tile.entities.remove(self)
        self.scene.entities.remove(self)


class Hourglass(Item):

    GLYPH = ItemType.HOURGLASS
    COLOR = Color.YELLOW

    def on_pickup(self):
        super().on_pickup()
        self.scene.player.state = ActorState.VICTORIOUS


class HealthPotion(Item):

    GLYPH = ItemType.POTION
    COLOR = Color.RED
    HP = 3

    def on_pickup(self):
        if self.scene.player.hp == self.scene.player.max_hp:
            self.scene.log("You're already at full health.")
            return
        # Only heal up to max hp
        if self.scene.player.hp + self.HP > self.scene.player.max_hp:
            self.scene.player.delta_hp += self.scene.player.max_hp - self.scene.player.hp
        else:
            self.scene.player.delta_hp += self.HP
        self.scene.player.hp_update()
        self.scene.print_stats(hp=True)
        super().on_pickup()


class TimePotion(Item):

    GLYPH = ItemType.POTION
    COLOR = Color.VIOLET
    TP = 3

    def on_pickup(self):
        if self.scene.player.tp == self.scene.player.max_tp:
            self.scene.log("Your time power is already full.")
            return
        if self.scene.player.tp + self.TP > self.scene.player.max_tp:
            self.scene.player.delta_tp += self.scene.player.max_tp - self.scene.player.tp
        else:
            self.scene.player.delta_tp += self.TP
        self.scene.player.tp_update()
        self.scene.print_stats(tp=True)
        super().on_pickup()
