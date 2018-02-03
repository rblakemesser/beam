from state import beam_state
from animations.base import BaseBeamAnim, check_interrupt, adjustable
import util as beam_util


class Light(BaseBeamAnim):
    """
    With one color, the strip is a single-colored light. With multiple,
    the colors just alternate along the strip (but are not animated).
    """

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = beam_state.colors[beam_util.get_location(x, y) % len(beam_state.colors)]
            self.layout.set(x, y, c)

        self._step = 0
