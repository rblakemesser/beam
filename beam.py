import random
import functools

from bibliopixel import log
from bibliopixel.layout import Matrix
from bibliopixel.drivers import SimPixel
from bibliopixel.animation.matrix import BaseMatrixAnim
from bibliopixel.animation.animation import STATE
import bibliopixel.colors as colors


log.setLogLevel(log.INFO)


PIXELS_PER_STRIP = 108
NUM_STRIPS = 2


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        if switch_input():
            raise Interrupt()
        return fn(*args, **kwargs)

    return wrapped


def switch_input():
    return random.random() < .01


class Interruptable(BaseMatrixAnim):
    def __init__(self, layout, delay):
        super().__init__(layout)
        self.set_delay(delay)

    def set_delay(self, delay):
        self.internal_delay = delay


class Rainbow(Interruptable):
    @check_interrupt
    def step(self, amt=1):
        for px in range(self.layout.numLEDs):
            row = px % PIXELS_PER_STRIP
            c = colors.wheel.wheel_color((self._step + row) % 384)
            self.layout._set_base(px, c)

        self._step += amt


class White(Interruptable):

    @check_interrupt
    def step(self, amt=1):
        for px in range(self.layout.numLEDs):
            row = px % PIXELS_PER_STRIP
            c = colors.COLORS.WHITE
            self.layout._set_base(px, c)

        self._step += amt


def get_new_input_class(key=None):
    animation_dict = {
        'rainbox': Rainbow,
        'white': White,
    }

    if key:
        return animation_dict[key]

    vals = list(animation_dict.values())
    return random.choice(vals)


def main_loop(led):
    while True:
        animation_class = get_new_input_class()
        speed = 0.05

        log.info('Starting {} animation at speed {}'.format(animation_class.__name__, speed))
        animation = animation_class(led, speed)
        animation.set_runner(None)

        try:
            animation.run_all_frames()
        except Interrupt:
            log.info('interrupt fired')


if __name__ == '__main__':
    driver = SimPixel.SimPixel(num=PIXELS_PER_STRIP * NUM_STRIPS)
    led = Matrix(driver, width=PIXELS_PER_STRIP, height=NUM_STRIPS, serpentine=False)

    main_loop(led)

