import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
import util as beam_util
import bibliopixel.colors as color_util
from state import beam_state


class ColorWipeSequential(BaseBeamAnim):

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            if beam_util.get_location(x, y) < self._step:
                self.layout.set(x, y, random.choice(beam_state.colors))
            else:
                self.layout.set(x, y, color_util.Off)

        if self._step == self.layout.width * self.layout.height:
            self._step = 0
        else:
            self._step += amt
