#!/usr/bin/env python

import sys

import Image

### Globals
LUT16to32 = [0] * 65536
RGBtoYUV = [0] * 65536
YUV1 = 0
YUV2 = 0
Ymask = 0x00FF0000
Umask = 0x0000FF00
Vmask = 0x000000FF
trY   = 0x00300000
trU   = 0x00000700
trV   = 0x00000006

for i in xrange(65536):
    LUT16to32[i] = ((i & 0xF800) << 8) + ((i & 0x07E0) << 5) + ((i & 0x001F) << 3)

for i in xrange(32):
    for j in xrange(64):
        for k in xrange(32):
            r = i << 3
            g = j << 2
            b = k << 3
            Y = (r + g + b) >> 2
            u = 128 + ((r - b) >> 2)
            v = 128 + ((-r + 2*g - b) >> 3)
            RGBtoYUV[ (i << 11) + (j << 5) + k ] = (Y << 16) + (u << 8) + v

### Main
infile, outfile = sys.argv[1:3]
print infile, outfile

source = Image.open(infile)
w, h = source.size
print source.format, source.size, source.mode

dest = Image.new(source.mode, (w * 2, h * 2))

# These give direct pixel access via grid[x, y]
sourcegrid = source.load()
destgrid = dest.load()

for x in xrange(w):
    for y in xrange(h):
        px = sourcegrid[x, y]
        destgrid[x * 2, y * 2] = px
        destgrid[x * 2 + 1, y * 2] = px
        destgrid[x * 2, y * 2 + 1] = px
        destgrid[x * 2 + 1, y * 2 + 1] = px

dest.show()
print sourcegrid[0, 0]
