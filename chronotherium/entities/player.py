from .entity import Actor, EntityType


class Player(Actor):

    TYPE = EntityType.PLAYER
    BASE_HP = 10
    BASE_TP = 5
