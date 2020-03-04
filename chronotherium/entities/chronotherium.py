from chronotherium.entities.entity import Actor, EntityType
from chronotherium.window import Color


class Chronotherium(Actor):

    NAME = "Chronotherium"
    DESCRIPTION = "A hulking mass of intricate shimmering filigree"
    TYPE = EntityType.ENEMY
    BASE_HP = 25
    BASE_TP = 10
    COLOR = Color.MAGENTA # Solorized
