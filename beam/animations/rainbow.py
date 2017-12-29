from animations.base import BaseBeamAnim, check_interrupt, adjustable
import bibliopixel.colors as color_util


class Rainbow(BaseBeamAnim):

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = color_util.wheel.wheel_color((self._step + x) % 384)
            self.layout.set(x, y, c)

        if self._step + amt == 384:
            self._step = 0
        else:
            self._step += amt
