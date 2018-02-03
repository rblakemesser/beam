from animations.base import BaseBeamAnim, check_interrupt, adjustable
import util as beam_util
from state import beam_state


class Strip(BaseBeamAnim):
    """
    Alternate the list of colors down the strip.
    """

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        color_length = len(beam_state.colors)
        for x, y in self.grid():
            col_color = beam_state.colors[(beam_util.get_location(x, y) + self._step) % color_length]
            self.layout.set(x, y, col_color)

        if self._step + amt == color_length:
            self._step = 0
        else:
            self._step += amt
