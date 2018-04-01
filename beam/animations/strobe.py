from beam.state import beam_state
from animations.base import BaseBeamAnim, check_interrupt, adjustable
import beam.util as beam_util


class Strobe(BaseBeamAnim):
    """
    """

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            if self._step % 2:
                c = beam_state.colors[beam_util.get_location(x, y) % len(beam_state.colors)]
            else:
                c = (0, 0, 0)
                
            self.layout.set(x, y, c)

        if self._step + amt == color_length:
            self._step = 0
        else:
            self._step += amt
