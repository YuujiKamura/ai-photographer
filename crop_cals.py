#!/usr/bin/env python3
"""Crop to 4:3 at specified top offset, then resize to CALS 1280x960."""
import sys
from PIL import Image

CALS_W, CALS_H = 1280, 960

path = sys.argv[1]
top = int(sys.argv[2])  # top offset in pixels

img = Image.open(path)
w, h = img.size
# crop to 4:3 based on available width
crop_h = int(w * 3 / 4)
img = img.crop((0, top, w, top + crop_h))
# resize to CALS
img = img.resize((CALS_W, CALS_H), Image.LANCZOS)
img.save(path)
print(f"cropped: {path} (top={top}, intermediate={w}x{crop_h})")
