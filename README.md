# clahelib

A Python library that implements a parallelized version of the [Contrast Limited Adaptive Histogram Equalization (CLAHE)](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization) algorithm on image types supported by Pillow, including 16 bpp grayscale and color images. 

The repo contains two .py files:
1) clahelib.py: Main library code.
2) clahe_test.py: An example of how to call the library and sample profiler code. The purpose of the profiler code is to measure library speed under different conditions such as number of processes used and algorithm parameters.

The images folder contains sample images along with CLAHE'd versions of the same. The code within clahe_test.py by default uses one of the images within this folder.

# Requirements

The code has been tested on both Windows 10 64-bit and Linux Mint 19 64-bit, both with Python 3.8. The library needs Pillow 7.2.0 for image processing, and ray 0.9.0 for parallelization purposes. The library might work with slightly older or newer versions of Pillow and ray, but your mileage might vary. As of 8/5/2020, the two following commands installed versions of the dependencies that worked harmoniously with the library:

    pip install Pillow
    pip install ray

If you'd like to run clahe_test.py you will need to make sure you have cProfile and pstats installed as well. I am aware, however, they are typically bundled with newer Python installations.
