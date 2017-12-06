import json
import ctypes
import random
import functools
import threading
import itertools
import platform
from enum import Enum
from flask_cors import CORS

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

env = 'dev' if platform.system() == 'Darwin' else 'prod'

PIXELS_PER_STRIP = 286 if env == 'prod' else 100
NUM_STRIPS = 2


class Animation(Enum):
    rainbow = 1
    light = 2
    bloom = 3
    strip = 4
    rain = 5
    kimbow = 6
    zap = 7

animation_names = list(map(lambda a: a.name, list(Animation)))

app = flask.Flask(__name__)
CORS(app)

delay = .05
brightness = 255
animation = Animation.light.value
colors = [color_util.hex2rgb('#ffffff')]


def _rgb_to_hex(rgb_list):
    """Return color as #rrggbb for the given color values."""
    red, green, blue = rgb_list
    return '#%02x%02x%02x' % (red, green, blue)


def _get_state():
    return {
        'brightness': brightness,
        'delay': delay,
        'animation': Animation(animation).name,
        'colors': list(map(_rgb_to_hex, colors)),
    }


@app.route('/', methods=['GET'])
def get_beam_state():
    return flask.Response(json.dumps(_get_state()), 200)


@app.route('/', methods=['POST'])
def change_beam_state():
    request_dict = flask.request.get_json()

    input_delay = request_dict.get('delay')
    if input_delay is not None and 0.0001 <= input_delay <= 10:
        global delay
        delay = input_delay

    input_brightness = request_dict.get('brightness')
    if input_brightness is not None and 0 <= input_brightness <= 255:
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
        response_dict = _get_state()

        return flask.Response(json.dumps(response_dict), 200)

    else:
        return flask.redirect('/')


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    """
    Decorator to check whether to kill animation between calls to step()
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        if animation and Animation(animation).name != self.name:
            log.info('changing from {} to {}'.format(self.name, Animation(animation).name))
            raise Interrupt('changing sequence')

        return fn(self, *args, **kwargs)

    return wrapped


def adjustable(fn):
    """
    Allows updating the delay and brightness between calls to step() from
    the globals
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        self.set_delay(delay)
        self.set_brightness(brightness)

        return fn(self, *args, **kwargs)

    return wrapped


def get_location(x, y):
    """
    Given x, y coordinates of a location, yield its ordinal position.
    Sometimes useful in step() functions.
    """
    return (y * PIXELS_PER_STRIP) + x


class BaseBeamAnim(BaseMatrixAnim):
    """
    Adds some convenience methods to the base class
    """
    def __init__(self, layout):
        super().__init__(layout)

    def set_delay(self, d):
        if d == self.internal_delay:
            return

        self.internal_delay = d

    def set_brightness(self, b):
        if b == self.layout.brightness:
            return

        self.layout.set_brightness(b)

    def grid(self):
        """
        Returns a generator that yields all pairwise x, y combinations
        in the matrix.
        """

        points = itertools.product(
            range(self.layout.width),
            range(self.layout.height),
        )
        return points


class Kimbow(BaseBeamAnim):
    name = Animation.kimbow.name

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = color_util.wheel.wheel_color((self._step + x + y) % 384)
            self.layout.set(x, y, c)

        self._step += amt


class Zap(BaseBeamAnim):
    name = Animation.zap.name

    def __init__(self, layout, dir=True):
        super().__init__(layout)

        # First color
        c_int = random.randint(0, len(colors) - 1)
        self.color = color = colors[c_int]

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        self.layout.all_off()

        tail_len = 40 # Whatever
        bullet_pos = self._step % (PIXELS_PER_STRIP + tail_len)

        for x, y in self.grid():
            if x <= bullet_pos and x > bullet_pos - tail_len:
                brightness = 255 - ((bullet_pos - x) * (255 / tail_len))
                self.layout.set(x, y, color_util.color_scale(self.color, brightness))

        if bullet_pos + 1 >= PIXELS_PER_STRIP + tail_len:
            # Sequence is about to end; Choose another color for the next ZAP
            c_int = random.randint(0, len(colors) - 1)
            self.color = color = colors[c_int]

        self._step += amt


class Rainbow(BaseBeamAnim):
    name = Animation.rainbow.name

    @check_interrupt
    @adjustable
    def step(self, amt=1):
        for x, y in self.grid():
            c = color_util.wheel.wheel_color((self._step + x) % 384)
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

    def __init__(self, layout, dir=True):
        super().__init__(layout)
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


class MatrixRain(BaseBeamAnim):
    name = Animation.rain.name
    def __init__(self, layout, tail=4, growth_rate=4):
        super(MatrixRain, self).__init__(layout)
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
            c_int = random.randint(0, len(colors) - 1)
            self._drops[new_drop].append((0, colors[c_int]))

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


def get_new_input_class(key=None):
    animation_dict = {
        Animation.rainbow.name: Rainbow,
        Animation.light.name: Light,
        Animation.bloom.name: Bloom,
        Animation.strip.name: Strip,
        Animation.rain.name: MatrixRain,
        Animation.kimbow.name: Kimbow,
        Animation.zap.name: Zap,
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
        anim = animation_class(led)
        anim.set_runner(None)

        log.info('starting {} sequence'.format(anim.name))

        try:
            anim.run_all_frames()
        except Interrupt:
            pass


if __name__ == '__main__':
    if env == 'dev':
        # simulator on osx
        driver = SimPixel.SimPixel(num=PIXELS_PER_STRIP * NUM_STRIPS)
    else:
        # hardware on pi
        driver = Serial(num=PIXELS_PER_STRIP * NUM_STRIPS, ledtype=LEDTYPE.WS2811, c_order=ChannelOrder.GRB)

    led = Matrix(
        driver,
        width=PIXELS_PER_STRIP,
        height=NUM_STRIPS,
        brightness=brightness,
        serpentine=True,
    )

    main_loop(led)
