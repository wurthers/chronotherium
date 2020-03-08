from chronotherium.entities.entity import Enemy, ActorType
from chronotherium.window import Color

from chronotherium.entities.items import TimePotion


class Golem(Enemy):

    NAME = "Hourglass Golem"
    DESCRIPTION = "Shifting sands spill from cracked fluted glass to form massive limbs."
    GLYPH = ActorType.GOLEM
    BASE_HP = 5
    BASE_TP = 2
    RANGE = 5
    XP = 6
    COLOR = Color.VIOLET
    DROP = TimePotion
    TP_DRAIN_RATE = 4
    TP_DRAIN_COST = 1

    def __init__(self, tile, map, scene):
        self._tp_drain_clock = 0
        super().__init__(tile, map, scene)

    def ai_behavior(self):
        if self.visible_to(self.scene.player):
            self.drain_tp()
        super().ai_behavior()

    def drain_tp(self):
        if self.tp < self.TP_DRAIN_COST:
            return
        self._tp_drain_clock += 1
        self.delta_tp -= self.TP_DRAIN_COST
        if self._tp_drain_clock % self.TP_DRAIN_RATE == 0:
            self.scene.player.delta_tp -= 2
            self.scene.player.update_tp()
            self.scene.log(f'The {self.NAME} drained your tp!')
