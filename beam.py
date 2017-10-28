import json
import random
import functools
import multiprocessing

import flask

from bibliopixel import log
from bibliopixel.layout import Matrix
from bibliopixel.drivers import SimPixel
from bibliopixel.animation.matrix import BaseMatrixAnim
from bibliopixel.animation.animation import STATE
import bibliopixel.colors as colors


log.setLogLevel(log.INFO)


PIXELS_PER_STRIP = 108
NUM_STRIPS = 2


app = flask.Flask(__name__)
delay = multiprocessing.Value('d', 0.05)
brightness = multiprocessing.Value('i', 255)


@app.route('/', methods=['POST'])
def change_beam_state():
    request_dict = json.loads(flask.request.data)

    input_delay = request_dict.get('delay')
    if input_delay and 0.0001 <= input_brightness <= 10::
        delay.value = input_delay

    input_brightness = request_dict.get('brightness')
    if input_brightness and 0 <= input_brightness <= 255:
        brightness.value = input_brightness

    response_dict = {
        'brightness': brightness.value,
        'delay': delay.value,
    }

    return flask.Response(json.dumps(response_dict), 200)


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    @functools.wraps(fn)
    def wrapped(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapped


class Interruptable(BaseMatrixAnim):
    def __init__(self, layout, d):
        super().__init__(layout)
        self.set_delay(d)

    def set_delay(self, d):
        if d == self.internal_delay:
            return

        log.info('setting the damn delay')
        self.internal_delay = d

    def set_brightness(self, b):
        if b == self.layout.brightness:
            return

        log.info('setting the damn brightness')
        self.layout.set_brightness(b)


class Rainbow(Interruptable):
    @check_interrupt
    def step(self, amt=1):
        self.set_delay(delay.value)
        self.set_brightness(brightness.value)
        for px in range(self.layout.numLEDs):
            row = px % PIXELS_PER_STRIP
            c = colors.wheel.wheel_color((self._step + row) % 384)
            self.layout._set_base(px, c)

        self._step += amt


class Light(Interruptable):
    @check_interrupt
    def step(self, amt=1):
        self.set_brightness(brightness.value)
        for px in range(self.layout.numLEDs):
            row = px % PIXELS_PER_STRIP
            c = colors.COLORS.WHITE
            self.layout._set_base(px, c)

        self._step += amt


def get_new_input_class(key=None):
    animation_dict = {
        'rainbow': Rainbow,
        'light': Light,
    }

    if key:
        return animation_dict[key]

    vals = list(animation_dict.values())
    return random.choice(vals)


def main_loop(led):
    p = multiprocessing.Process(target=app.run, kwargs={'port': 5555}, daemon=True)
    p.start()

    while True:
        animation_class = get_new_input_class('rainbow')
        animation = animation_class(led, delay.value)
        animation.set_runner(None)

        log.info('starting new sequence')

        try:
            animation.run_all_frames()
        except Interrupt:
            log.info('interrupt fired')


if __name__ == '__main__':
    driver = SimPixel.SimPixel(num=PIXELS_PER_STRIP * NUM_STRIPS)
    led = Matrix(driver, width=PIXELS_PER_STRIP, height=NUM_STRIPS, brightness=brightness.value, serpentine=False)

    main_loop(led)

