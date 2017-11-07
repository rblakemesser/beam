import json
import ctypes
import random
import functools
import threading
import itertools
from enum import Enum

import flask

from bibliopixel import log
from bibliopixel.layout import Matrix
from bibliopixel.drivers import SimPixel
from bibliopixel.animation.matrix import BaseMatrixAnim
from bibliopixel.animation.animation import STATE
from bibliopixel.util import genVector
from bibliopixel.animation import MatrixCalibrationTest

from bibliopixel.drivers.serial import Serial, LEDTYPE
from bibliopixel.drivers.channel_order import ChannelOrder
import bibliopixel.colors as color_util


log.setLogLevel(log.INFO)


PIXELS_PER_STRIP = 36
NUM_STRIPS = 2


class Animation(Enum):
    rainbow = 1
    light = 2
    bloom = 3
    strip = 4

animation_names = list(map(lambda a: a.name, list(Animation)))

app = flask.Flask(__name__)

delay = .05
brightness = 255
animation = Animation.rainbow.value
colors = [color_util.hex2rgb('#ffffff')]


@app.route('/', methods=['POST'])
def change_beam_state():
    request_dict = json.loads(flask.request.data) if flask.request.data else flask.request.form

    input_delay = request_dict.get('delay')
    if input_delay and 0.0001 <= input_delay <= 10:
        global delay
        delay = input_delay

    input_brightness = request_dict.get('brightness')
    if input_brightness and 0 <= input_brightness <= 255:
        global brightness
        brightness = input_brightness

    input_animation = request_dict.get('animation')
    if input_animation in animation_names:
        global animation
        animation = Animation[input_animation].value
    else:
        log.info('unknown animation: {}'.format(input_animation))

    input_colors = request_dict.get('colors', [])
    if input_colors:
        try:
            input_colors = list(map(color_util.hex2rgb, input_colors))
            global colors
            colors = input_colors
        except KeyError:
            log.info('invalid color passed')

    if flask.request.data:
        response_dict = {
            'brightness': brightness,
            'delay': delay,
            'animation': Animation(animation).name,
            'colors': colors,
        }

        return flask.Response(json.dumps(response_dict), 200)
    else:
        return flask.redirect('/')


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        if animation and Animation(animation).name != self.name:
            log.info('changing from {} to {}'.format(self.name, Animation(animation).name))
            raise Interrupt('changing sequence')

        return fn(self, *args, **kwargs)

    return wrapped


def adjustable(fn):
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        self.set_delay(delay)
        self.set_brightness(brightness)

        return fn(self, *args, **kwargs)

    return wrapped


class BaseBeamAnim(BaseMatrixAnim):
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

    def grid(self):
        points = itertools.product(
            range(self.layout.width),
            range(self.layout.height),
        )
        return points


def get_location(x, y):
    return (y * PIXELS_PER_STRIP) + x


class Rainbow(BaseBeamAnim):
    name = Animation.rainbow.name

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = color_util.wheel.wheel_color((self._step + y) % 384)
            self.layout.set(x, y, c)

        self._step += amt


class Light(BaseBeamAnim):
    """
    With one color, the strip is a single-colored light. With multiple,
    the colors just alternate along the strip (but are not animated).
    """

    name = Animation.light.name

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = colors[get_location(x, y) % len(colors)]
            self.layout.set(x, y, c)

        self._step += amt


class Strip(BaseBeamAnim):
    """
    Alternate the list of colors down the strip.
    """

    name = Animation.strip.name

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            col_color = colors[(get_location(x, y) + self._step) % len(colors)]
            self.layout.set(x, y, col_color)

        self._step += amt


class Bloom(BaseBeamAnim):
    """
    Adapted from Maniacal labs animation lib
    """

    name = Animation.bloom.name

    def __init__(self, layout, d, dir=True):
        super().__init__(layout, d)
        self._vector = genVector(self.layout.width, self.layout.height)
        self._dir = dir

    @check_interrupt
    @adjustable
    def step(self, amt=8):
        if self._dir:
            s = 255 - self._step
        else:
            s = self._step

        # this respects master brightness but is slower
        for y in range(self.layout.height):
            for x in range(self.layout.width):
                c = color_util.hue_helper(self._vector[y][x], self.layout.height, s)
                self.layout.set(x, y, c)

        self._step += amt
        if self._step >= 255:
            self._step = 0


def get_new_input_class(key=None):
    animation_dict = {
        Animation.rainbow.name: Rainbow,
        Animation.light.name: Light,
        Animation.bloom.name: Bloom,
        Animation.strip.name: Strip,
    }

    if key:
        animation_name = Animation(key).name
        return animation_dict[animation_name]

    vals = list(animation_dict.values())
    return random.choice(vals)


def main_loop(led):
    t = threading.Thread(target=app.run, kwargs={'port': 5555}, daemon=True)
    t.start()

    while True:
        animation_class = get_new_input_class(animation)
        anim = animation_class(led, delay)
        anim.set_runner(None)

        log.info('starting {} sequence'.format(anim.name))

        try:
            anim.run_all_frames()
        except Interrupt:
            pass


if __name__ == '__main__':
    driver = SimPixel.SimPixel(num=PIXELS_PER_STRIP * NUM_STRIPS)
    # driver = Serial(num=PIXELS_PER_STRIP * NUM_STRIPS, ledtype=LEDTYPE.WS2811, c_order=ChannelOrder.GRB)

    led = Matrix(
        driver,
        width=PIXELS_PER_STRIP,
        height=2,
        brightness=brightness,
        serpentine=True,
    )

    main_loop(led)
