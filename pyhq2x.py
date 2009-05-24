#!/usr/bin/env python

import Image

# Constants for indicating coordinates in a pixel's context
TOP_LEFT = 0
TOP = 1
TOP_RIGHT = 2
LEFT = 3
CENTER = 4
RIGHT = 5
BOTTOM_LEFT = 6
BOTTOM = 7
BOTTOM_RIGHT = 8

# Constants defining how far apart two components of YUV colors must be to be
# considered different
Y_THRESHHOLD = 48
U_THRESHHOLD = 7
V_THRESHHOLD = 6

rgb_yuv_cache = {}  # memoization
def rgb_to_yuv(rgb):
    """Takes a tuple of (r, g, b) and returns a tuple (y, u, v).  Both must be
    24-bit color!

    This is the algorithm from the original hq2x source; it doesn't seem to
    match any other algorithm I can find, but whatever.
    """

    if rgb in rgb_yuv_cache:
        return rgb_yuv_cache[rgb]

    r, g, b = rgb

    y = (r + g + b) >> 2
    u = 128 + ((r - b) >> 2)
    v = 128 + ((-r + g * 2 - b) >> 3)

    rgb_yuv_cache[rgb] = y, u, v
    return y, u, v


def yuv_equal(a, b):
    """Takes two tuples of (y, u, v).  Returns True if they are equal-ish,
    False otherwise.  "Equal-ish" is defined arbitrarily as tolerating small
    differences in the components of the two colors.
    """
    ay, au, av = a
    by, bu, bv = b
    if abs(ay - by) > Y_THRESHHOLD:
        return False
    if abs(au - bu) > U_THRESHHOLD:
        return False
    if abs(av - bv) > V_THRESHHOLD:
        return False

    return True


def hq2x(source):
    """Upscales a sprite image using the hq2x algorithm.

    Argument is an Image object containing the source image.  Returns another
    Image object containing the upscaled image.
    """

    w, h = source.size
    mode = source.mode  # XXX use this for the target I guess somehow; palette?
    source = source.convert('RGB')
    dest = Image.new('RGB', (w * 2, h * 2))

    # These give direct pixel access via grid[x, y]
    sourcegrid = source.load()
    destgrid = dest.load()

    # Wrap sourcegrid in a function to cap the coordinates; we need a 3x3 array
    # centered on the current pixel, and factoring out the capping is simpler
    # than a ton of ifs
    def get_px(x, y):
        if x < 0:
            x = 0
        elif x >= w:
            x = w - 1

        if y < 0:
            y = 0
        elif y >= h:
            y = h - 1

        return sourcegrid[x, y]

    for x in xrange(w):
        for y in xrange(h):
            px = sourcegrid[x, y]
            yuv_px = rgb_to_yuv(px)

            # This is a flattened 3x3 grid with the current pixel in the
            # middle; if the pixel is on an edge, the row/column in the void is
            # just a copy of the edge
            context = [
                get_px(x - 1, y - 1), get_px(x, y - 1), get_px(x + 1, y - 1),
                get_px(x - 1, y    ), get_px(x, y    ), get_px(x + 1, y    ),
                get_px(x - 1, y + 1), get_px(x, y + 1), get_px(x + 1, y + 1),
            ]
            yuv_context = [rgb_to_yuv(rgb) for rgb in context]

            # The massive lookup table is keyed on a bitstring where each bit
            # corresponds to an element in the context.  The top left is 0x1,
            # top middle is 0x2, and so on across and down.  Bits turned on
            # indicate a pixel different from the current pixel
            pattern = 0
            for bit in xrange(9):
                if bit != CENTER and not yuv_equal(yuv_context[bit], yuv_px):
                    pattern = pattern & (1 << bit)

            destgrid[x * 2, y * 2] = px
            destgrid[x * 2 + 1, y * 2] = px
            destgrid[x * 2, y * 2 + 1] = px
            destgrid[x * 2 + 1, y * 2 + 1] = px

    return dest


### Main, if called from command line
if __name__ == '__main__':
    import sys

    infile, outfile = sys.argv[1:3]
    source = Image.open(infile)

    dest = hq2x(source)

    dest.show()
