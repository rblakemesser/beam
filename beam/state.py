from config import config
import bibliopixel.colors as color_util


__all__ = ['beam_state']


class BeamState(object):
    def __init__(self):
        self.delay = config.initial_delay
        self.brightness = config.initial_brightness
        self.animation = config.initial_animation
        beam_colors = config.initial_colors or ['#ff0000', '#00ff00', '#0000ff']
        self.colors = list(map(color_util.hex2rgb, beam_colors))

beam_state = BeamState()
