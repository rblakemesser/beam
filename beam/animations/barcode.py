import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
import bibliopixel.colors as color_util

class Barcode(BaseBeamAnim):

    p = 10

    def __init__(self, layout):
        super().__init__(layout)

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        if self._step == 0:
            self.new_barcode()

        if self._step == self.p:
            for x in range(0, self.layout.width):
                self.layout.set(x, int(self.layout.height / 2), (255, 0, 0))
            self._step = 0
        else:
            self._step += amt

    def new_barcode(self):
        b = []
        for n in range(0, self.layout.width):
            b.append(random.randint(0, 1))
        for x, y in self.grid():
            self.layout.set(x, y, (b[x] * 255, b[x] * 255, b[x] * 255))
