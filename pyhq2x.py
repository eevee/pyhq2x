#!/usr/bin/env python

import sys

import Image

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
