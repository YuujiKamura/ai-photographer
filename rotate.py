#!/usr/bin/env python3
"""Rotate 90° CW only (no crop)."""
import sys
from PIL import Image

for path in sys.argv[1:]:
    try:
        img = Image.open(path)
        img = img.rotate(-90, expand=True)
        img.save(path)
        print(f"rotated: {path}")
    except Exception as e:
        print(f"error: {path}: {e}")
