from animations.base import BaseBeamAnim, check_interrupt, adjustable


class Light(BaseBeamAnim):
    """
    With one color, the strip is a single-colored light. With multiple,
    the colors just alternate along the strip (but are not animated).
    """

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = beam_state.colors[get_location(x, y) % len(beam_state.colors)]
            self.layout.set(x, y, c)

        self._step = 0
