import os
import json


__all__ = ['config']


class ConfigError(Exception):
    pass


env_path = '/home/pi/workspace/beam/.env'
if not os.path.exists(env_path):
    env_path = '.env'

if os.path.exists(env_path):
    with open(env_path) as fhandle:
        env_vars = json.loads(fhandle.read())


Config = type('Config', (), {})
config = Config()

config.pixels_per_strip = env_vars.get('PIXELS_PER_STRIP', 40)
config.num_strips = env_vars.get('NUM_STRIPS', 2)
config.max_brightness = env_vars.get('MAX_BRIGHTNESS', 255)
config.channel_order = env_vars.get('CHANNEL_ORDER', 'GRB')
config.driver = env_vars.get('DRIVER', 'sim')

config.initial_brightness = env_vars.get('INITIAL_BRIGHTNESS', config.max_brightness)
config.initial_animation = env_vars.get('INITIAL_ANIMATION', 'Light')
config.initial_delay = float(env_vars.get('INITIAL_DELAY', ".05"))
config.initial_colors = env_vars.get('INITIAL_COLORS')


if config.initial_brightness > config.max_brightness:
    raise ConfigError('initial brightness cannot be greater than max_brightness')
