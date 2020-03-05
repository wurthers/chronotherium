from abc import ABC

from chronotherium.entities.entity import Entity, EntityType, ItemType, ActorState
from chronotherium.entities.player import Player


class Item(Entity, ABC):

    TYPE = EntityType.ITEM

    def on_pickup(self, player: Player):
        raise NotImplementedError('Items must implement on_pickup!')


class Hourglass(Item):

    GLYPH = ItemType.HOURGLASS

    def on_pickup(self, player: Player):
        self.player.state = ActorState.VICTORIOUS


class HealthPotion(Item):

    GLYPH = ItemType.POTION
    HP = 2

    def on_pickup(self, player: Player):
        self.player.delta_hp += self.HP
