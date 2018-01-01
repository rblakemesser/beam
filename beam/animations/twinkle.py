import random
from animations.base import BaseBeamAnim, check_interrupt, adjustable
from beam.state import beam_state
import bibliopixel.colors as color_util


class Twinkle(BaseBeamAnim):

    def __init__(self, layout, dir=True):
        super().__init__(layout)

        self.layout = layout
        self.colors = beam_state.colors
        self.density = 20
        self.speed = 2
        self.max_bright = 255

        # Make sure speed, density & max_bright are in sane ranges
        self.speed = min(self.speed, 100)
        self.speed = max(self.speed, 2)
        self.density = min(self.density, 100)
        self.density = max(self.density, 2)
        self.max_bright = min(self.max_bright, 255)
        self.max_bright = max(self.max_bright, 5)

    def pre_run(self):
        self._step = 0
        # direction, color, level
        self.pixels = [(0, color_util.Off, 0)] * self.layout.numLEDs

    def pick_led(self, speed):
        idx = random.randrange(0, self.layout.numLEDs)
        p_dir, p_color, p_level = self.pixels[idx]

        if random.randrange(0, 100) < self.density:
            if p_dir == 0:  # 0 is off
                p_level += speed
                p_dir = 1  # 1 is growing
                p_color = random.choice(self.colors)
                self.layout._set_base(idx, color_util.color_scale(p_color, p_level))

                self.pixels[idx] = p_dir, p_color, p_level

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        self.layout.all_off()
        self.pick_led(self.speed)

        for i, val in enumerate(self.pixels):
            p_dir, p_color, p_level = val
            if p_dir == 1:
                p_level += self.speed
                if p_level > 255:
                    p_level = 255
                    p_dir = 2  # start dimming
                self.layout._set_base(i, color_util.color_scale(p_color, p_level))
            elif p_dir == 2:
                p_level -= self.speed
                if p_level < 0:
                    p_level = 0
                    p_dir = 0  # turn off
                self.layout._set_base(i, color_util.color_scale(p_color, p_level))

            self.pixels[i] = (p_dir, p_color, p_level)

        self._step += amt
