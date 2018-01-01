import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
from beam.state import beam_state
import beam.util as beam_util
import bibliopixel.colors as color_util


class Rain(BaseBeamAnim):

    def __init__(self, layout, tail=4, growth_rate=4):
        super().__init__(layout)
        self._tail = tail
        self._growth_rate = growth_rate

    def pre_run(self):
        self._drops = [[] for x in range(self.layout.width)]

    def _draw_drop(self, y, x, color):
        for i in range(self._tail):
            if x - i >= 0 and x - i < self.layout.width:
                level = 255 - ((255 // self._tail) * i)
                self.layout.set(x - i, y, color_util.color_scale(color, level))

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        self.layout.all_off()

        for i in range(self._growth_rate):
            new_drop = random.randint(0, self.layout.width - 1)
            c_int = random.randint(0, len(beam_state.colors) - 1)
            self._drops[new_drop].append((0, beam_state.colors[c_int]))

        for y in range(self.layout.height):
            row = self._drops[y]
            if not row:
                pass

            removals = []
            for x in range(len(row)):
                drop = row[x]
                if drop[0] < self.layout.width:
                    self._draw_drop(y, drop[0], drop[1])
                if drop[0] - (self._tail - 1) < self.layout.width:
                    drop = (drop[0] + 1, drop[1])
                    self._drops[y][x] = drop
                else:
                    removals.append(drop)

            for r in removals:
                self._drops[y].remove(r)

        self._step = 0
