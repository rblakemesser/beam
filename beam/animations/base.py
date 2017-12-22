import itertools
import functools
from bibliopixel.animation.matrix import BaseMatrixAnim
from bibliopixel import log

from beam.state import beam_state


__all__ = ['BaseBeamAnim', 'check_interrupt', 'adjustable', 'animation_dict']


animation_dict = {}


class AnimationMeta(type):
    def __init__(cls, name, bases, dct):
        # a little brittle
        if 'BaseBeamAnim' in map(lambda b: b.__name__, bases):
            animation_dict[cls.__name__] = cls

        return super(AnimationMeta, cls).__init__(name, bases, dct)


class Interrupt(Exception):
    pass


def check_interrupt(fn):
    """
    Decorator to check whether to kill animation between calls to step()
    """
    @functools.wraps(fn)
    def wrapped(self, *args, **kwargs):
        if beam_state.animation and beam_state.animation != self.__class__.__name__:
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
        if self.internal_delay != beam_state.delay:
            log.info('delay changing from {} to {}'.format(self.internal_delay, beam_state.delay))
        self.set_delay(beam_state.delay)
        self.set_brightness(beam_state.brightness)

        if self._step > 10000000:
            self._step = 0

        return fn(self, *args, **kwargs)

    return wrapped


class BaseBeamAnim(BaseMatrixAnim, metaclass=AnimationMeta):
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
