import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable


class LangtonsAnt(BaseBeamAnim):

    def __init__(self, layout):
        super().__init__(layout)
        self.offColor = color_util.Off
        self.curColor = self.offColor

    def pre_run(self):
        self.x = random.randrange(self.width)
        self.y = random.randrange(self.height)
        self.d = random.randrange(4)

    def __rollValue(self, val, step, _min, _max):
        val += step
        if val < _min:
            diff = _min - val
            val = _max - diff + 1
        elif val > _max:
            diff = val - _max
            val = _min + diff - 1
        return val

    def __changeDir(self, direction):
        direction = random.choice([1, -1])
        self.d = self.__rollValue(self.d, direction, 0, 3)

    def __moveAnt(self):
        if self.d == 0:
            self.y = self.__rollValue(self.y, 1, 0, self.height - 1)
        elif self.d == 1:
            self.x = self.__rollValue(self.x, 1, 0, self.width - 1)
        elif self.d == 2:
            self.y = self.__rollValue(self.y, -1, 0, self.height - 1)
        elif self.d == 3:
            self.x = self.__rollValue(self.x, -1, 0, self.width - 1)

        self.curColor = self.layout.get(self.x, self.y)
        self.layout.set(self.x, self.y, beam_state.colors[0])

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        pathColors = beam_state.colors[1:] if len(beam_state.colors) > 1 else [color_util.Green]
        if self.curColor in pathColors:
            self.layout.set(self.x, self.y, self.offColor)
            self.__changeDir(False)
            self.__moveAnt()
        else:
            self.layout.set(self.x, self.y, random.choice(pathColors))
            self.__changeDir(True)
            self.__moveAnt()
