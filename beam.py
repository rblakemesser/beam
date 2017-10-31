import json
import ctypes
import random
import functools
import multiprocessing
from enum import Enum

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


class Animation(Enum):
    rainbow = 1
    light = 2


app = flask.Flask(__name__)
delay = multiprocessing.Value('d', 0.05)
brightness = multiprocessing.Value('i', 255)
animation = multiprocessing.Value('d', Animation.rainbow.value)


@app.route('/', methods=['POST'])
def change_beam_state():
    request_dict = json.loads(flask.request.data)

    input_delay = request_dict.get('delay')
    if input_delay and 0.0001 <= input_delay <= 10:
        delay.value = input_delay

    input_brightness = request_dict.get('brightness')
    if input_brightness and 0 <= input_brightness <= 255:
        brightness.value = input_brightness

    input_animation = request_dict.get('animation')
    if input_animation in {'rainbow', 'light'}:
        animation.value = Animation[input_animation].value

    response_dict = {
        'brightness': brightness.value,
        'delay': delay.value,
        'animation': Animation(animation.value).name,
    }

    return flask.Response(json.dumps(response_dict), 200)


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        if animation.value and Animation(animation.value).name != self.name:
            log.info('changing from {} to {}'.format(self.name, Animation(animation.value).name))
            raise Interrupt('changing sequence')

        return fn(self, *args, **kwargs)

    return wrapped


class Interruptable(BaseMatrixAnim):
    def __init__(self, layout, d):
        super().__init__(layout)
        self.set_delay(d)

    def set_delay(self, d):
        if d == self.internal_delay:
            return

        self.internal_delay = d

    def set_brightness(self, b):
        if b == self.layout.brightness:
            return

        self.layout.set_brightness(b)


class Rainbow(Interruptable):
    name = 'rainbow'

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
    name = 'light'

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
        animation_name = Animation(key).name
        return animation_dict[animation_name]

    vals = list(animation_dict.values())
    return random.choice(vals)


def main_loop(led):
    p = multiprocessing.Process(target=app.run, kwargs={'port': 5555}, daemon=True)
    p.start()

    while True:
        animation_class = get_new_input_class(animation.value)
        anim = animation_class(led, delay.value)
        anim.set_runner(None)

        log.info('starting {} sequence'.format(anim.name))

        try:
            anim.run_all_frames()
        except Interrupt:
            pass


if __name__ == '__main__':
    driver = SimPixel.SimPixel(num=PIXELS_PER_STRIP * NUM_STRIPS)
    led = Matrix(driver, width=PIXELS_PER_STRIP, height=NUM_STRIPS, brightness=brightness.value, serpentine=False)

    main_loop(led)

