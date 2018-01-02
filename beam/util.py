from config import config


def get_location(x, y):
    """
    Given x, y coordinates of a location, yield its ordinal position.
    Sometimes useful in step() functions.
    """
    return (y * config.pixels_per_strip) + x


def rgb_to_hex(rgb_list):
    """Return color as #rrggbb for the given color values."""
    red, green, blue = rgb_list
    return '#%02x%02x%02x' % (red, green, blue)
