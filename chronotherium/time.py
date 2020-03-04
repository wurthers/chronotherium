class Time:

    MAX_RECORD = 10

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            new_window = super().__new__(cls)
            new_window.__init()
            cls.__instance = new_window
        return cls.__instance

    def __init(self):
        self._time = 0

    @property
    def time(self):
        return self._time

    def tick(self):
        self._time += 1
        return self._time

    def clock(self, tick: int = None):
        time = tick if tick is not None else self._time
        seconds = time % 60
        minutes = int((self._time - seconds) / 60)
        s = ''
        return f'{minutes}:{0 if seconds < 10 else s}{seconds}'


class TimeError(Exception):
    pass
