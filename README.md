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

# Installation

For now, a way to make sure the library can work with your software, is to ensure the file can be found by your own code. This would entail cloning the repo into your system and copying the clahelib.py file into a specific folder. A pip package might be provided in the future for easier installation.

# Usage

Add the following to the top of your Python code:

    import clahelib

You then have the option of calling clahe_color or clahe_bw depending on how you want to treat your input image. clahe_color will convert your image to the HSV color space and execute the CLAHE algorithm on the V component, then return an image in the original color space. clahe_bw will take in 8 bpp or 16 bpp grayscale images and execute the CLAHE algorithm. The returned image will be in the original color space. If the image passed as input to clahe_bw is not 8 bpp or 16 bpp grayscale, it will be converted to 8 bpp grayscale and the resulting CLAHE image will be returned as an 8 bpp grayscale image.

Both methods accept the following parameters:

    clahe_bw(image, blockSize, bins, slope, processes=0)
    clahe_color(image, blockSize, bins, slope, processes=0)
    
* image is the Pillow image you would like to run CLAHE on.
* blockSize is the size of the local region around a pixel for which the histogram is equalized. This size should be larger than the size of features to be preserved in the image. If unsure, try (width of image)/4.
* bins is the number of histogram bins used for histogram equalization. The number of histogram bins should be smaller than the number of pixels in a block (blockSize^2). If unsure, try 256.
* slope limits the contrast stretch in the intensity transfer function. A value of 1.0 will result in the original image. If unsure, try 2.0.
* processes (optional) sets the number of processes to subdivide tasks across CPU cores. A value of 1 is essentially a serial version of the algorithm. Not setting this parameter or setting it to 0 will use (#cpu_cores - 1) processes. If you are running the algorithm on a CPU with one core and you set processes to 0, the algorithm will only create one process.
