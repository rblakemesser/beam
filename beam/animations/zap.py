import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
from state import beam_state
import bibliopixel.colors as color_util


class Zap(BaseBeamAnim):

    def __init__(self, layout, dir=True):
        super().__init__(layout)

        # First color
        c_int = random.randint(0, len(beam_state.colors) - 1)
        self.color = color = beam_state.colors[c_int]

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        self.layout.all_off()

        tail_len = 40 # Whatever
        bullet_pos = self._step % (self.layout.width + tail_len)

        for x, y in self.grid():
            if x <= bullet_pos and x > bullet_pos - tail_len:
                beam_state.brightness = 255 - ((bullet_pos - x) * (255 / tail_len))
                self.layout.set(x, y, color_util.color_scale(self.color, beam_state.brightness))

        if bullet_pos + 1 >= self.layout.width + tail_len:
            # Sequence is about to end; Reset the Zap!
            c_int = random.randint(0, len(beam_state.colors) - 1)
            self.color = color = beam_state.colors[c_int]
            self._step = 0
        else:
            self._step += amt
