import os
import math
import time
import json
import enum
import ctypes
import random
import platform
import functools
import threading
import itertools

from flask_cors import CORS

import flask

from bibliopixel import log
from bibliopixel.layout import Matrix
from bibliopixel.drivers import SimPixel
from bibliopixel.animation.animation import STATE
from bibliopixel.animation import MatrixCalibrationTest

from bibliopixel.drivers.serial import Serial, LEDTYPE
from bibliopixel.drivers.channel_order import ChannelOrder
import bibliopixel.colors as color_util

from config import config
from animations.base import animation_dict, Interrupt
from state import beam_state
import util as beam_util

log.setLogLevel(log.INFO)

app = flask.Flask(__name__)
CORS(app)


Animation = enum.Enum('Animation', ' '.join(animation_dict.keys()))


def get_new_input_class(key=None):
    if key:
        return animation_dict[key]

    vals = list(animation_dict.values())
    return random.choice(vals)


def main_loop(led):
    t = threading.Thread(target=app.run, kwargs={'port': 5555}, daemon=True)
    t.start()

    while True:
        animation_class = get_new_input_class(beam_state.animation)
        anim = animation_class(led)
        anim.set_runner(None)

        log.info('starting {} sequence'.format(anim.__class__.__name__))

        try:
            anim.run_all_frames()
        except Interrupt:
            pass


def _get_state():
    return {
        'brightness': beam_state.brightness,
        'delay': beam_state.delay,
        'animation': beam_state.animation,
        'colors': list(map(beam_util.rgb_to_hex, beam_state.colors)),
    }


@app.route('/api/', methods=['GET'])
def get_beam_state():
    return flask.Response(json.dumps(_get_state()), 200)


@app.route('/api/', methods=['POST'])
def change_beam_state():
    request_dict = flask.request.get_json()

    input_delay = request_dict.get('delay')
    if input_delay is not None and 0.0001 <= input_delay <= 100:
        beam_state.delay = input_delay

    input_brightness = request_dict.get('brightness')
    if input_brightness is not None and 0 <= input_brightness <= 255:
        beam_state.brightness = math.floor(input_brightness * (config.max_brightness / 255.))

    input_animation = request_dict.get('animation')
    if input_animation in animation_dict.keys():
        beam_state.animation = input_animation
        log.info('setting beam_state.animation to {}'.format(input_animation))
    else:
        log.info('unknown animation: {}'.format(input_animation))

    input_colors = request_dict.get('colors', [])
    if input_colors:
        try:
            input_colors = list(map(color_util.hex2rgb, input_colors))
            beam_state.colors = input_colors
        except KeyError:
            log.info('invalid color passed')

    if flask.request.data:
        response_dict = _get_state()

        return flask.Response(json.dumps(response_dict), 200)

    else:
        return flask.redirect('/')


if __name__ == '__main__':

    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('--animation', '-a')
    parser.add_argument('--delay', '-d', type=float)
    parser.add_argument('--brightness', '-b', type=int)
    args = parser.parse_args()

    if args.animation:
        beam_state.animation = args.animation
    if args.brightness:
        beam_state.brightness = math.floor(args.brightness * (config.max_brightness / 255.))
    if args.delay:
        beam_state.delay = args.delay

    num_pixels = config.pixels_per_strip * config.num_strips
    if config.driver == 'sim':
        # simulator on osx
        log.info('using sim driver')
        driver = SimPixel.SimPixel(num=num_pixels)
    else:
        # hardware on pi
        c_order = getattr(ChannelOrder, config.channel_order)
        log.info('using neopixel driver with channel order: {}'.format(c_order))
        driver = Serial(num=num_pixels, ledtype=LEDTYPE.WS2811, c_order=c_order)

    led = Matrix(
        driver,
        width=config.pixels_per_strip,
        height=config.num_strips,
        brightness=beam_state.brightness,
        serpentine=True,
    )

    main_loop(led)
