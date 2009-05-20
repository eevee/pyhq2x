#!/usr/bin/env python

import Image

def rgb_to_yuv(rgb):
    """Takes a tuple of (r, g, b) and returns a tuple (y, u, v).  Both must be
    24-bit color!
    
    This is the algorithm from the original hq2x source; it doesn't seem to
    match any other algorithm I can find, but whatever.
    """

    if len(rgb) == 4:
        # Might be rgba
        r, g, b, a = rgb
    else:
        r, g, b = rgb

    y = (r + g + b) >> 2
    u = 128 + ((r - b) >> 2)
    v = 128 + ((-r + g * 2 - b) >> 3)
    return y, u, v


def hq2x(source):
    """Upscales a sprite image using the hq2x algorithm.

    Argument is an Image object containing the source image.  Returns another
    Image object containing the upscaled image.
    """

    w, h = source.size
    dest = Image.new(source.mode, (w * 2, h * 2))

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
            # This is a 3x3 grid with the current pixel in the middle; if the
            # pixel is on an edge, the row/column in the void is just a copy of
            # the edge
            context = [
                [get_px(x - 1, y - 1), get_px(x, y - 1), get_px(x + 1, y - 1)],
                [get_px(x - 1, y    ), get_px(x, y    ), get_px(x + 1, y    )],
                [get_px(x - 1, y + 1), get_px(x, y + 1), get_px(x + 1, y + 1)],
            ]
            yuv_context = [[rgb_to_yuv(rgb) for rgb in row] for row in context]

            px = sourcegrid[x, y]
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
