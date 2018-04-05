from animations.base import BaseBeamAnim, check_interrupt, adjustable
import bibliopixel.colors as color_util


class Rainbow(BaseBeamAnim):

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            hsv = ((self._step + x) % 255, 255, 255)
            c = color_util.hsv2rgb(hsv)
            self.layout.set(x, y, c)

        if self._step + amt == 255:
            self._step = 0
        else:
            self._step += amt * 2
