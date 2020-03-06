from abc import ABC

from chronotherium.entities.entity import Entity, EntityType, ItemType, ActorState


class Item(Entity, ABC):

    TYPE = EntityType.ITEM
    BLOCKING = False

    def __init__(self, position, map, scene):
        super().__init__(position, map, scene)
        self.scene.entities.append(self)

    def on_pickup(self):
        self.scene.entities.remove(self)


class Hourglass(Item):

    GLYPH = ItemType.HOURGLASS

    def on_pickup(self):
        super().on_pickup()
        self.scene.player.state = ActorState.VICTORIOUS


class HealthPotion(Item):

    GLYPH = ItemType.POTION
    HP = 2

    def on_pickup(self):
        super().on_pickup()
        self.scene.player.delta_hp += self.HP
