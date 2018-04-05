from animations.base import BaseBeamAnim, check_interrupt, adjustable
import bibliopixel.colors as color_util


class RainbowStrobe(BaseBeamAnim):

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            if not self._step % 2:
                hsv = ((self._step + x) % 255, 255, 255)
                c = color_util.hsv2rgb(hsv)
            else:
                c = (0, 0, 0)
            self.layout.set(x, y, c)

        if self._step + amt == 255:
            self._step = 0
        else:
            self._step += amt * 8
