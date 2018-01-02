import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
import bibliopixel.colors as color_util
from beam.state import beam_state


class ColorWipeRotate(BaseBeamAnim):

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            if self._step - self.layout.width < x < self._step:
                self.layout.set(x, y, random.choice(beam_state.colors))
            else:
                self.layout.set(x, y, color_util.Off)

        if self._step >= 2 * (self.layout.width - 1):
            self._step = 0
        else:
            self._step += amt
