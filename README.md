# CLAHE Library

A Python library that implements a parallelized version of the [Contrast Limited Adaptive Histogram Equalization (CLAHE)](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization) algorithm on image types supported by Pillow, including 16 bpp grayscale and color images. Please look at clahe_test.py to understand how to call the library. The code has been tested on both Windows 10 64-bit and Linux Mint 19 64-bit, both with Python 3.8.

Install Pillow and ray before using:

    pip install Pillow
    pip install ray
