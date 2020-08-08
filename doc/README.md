# clahelib's Developer's Documentation

## Overview

A Python library that implements a parallelized version of the [Contrast Limited Adaptive Histogram Equalization (CLAHE)](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization) algorithm on image types supported by Pillow, including 16 bpp grayscale and color images. I would highly recommend prospective developers read the top-level README file, as it contains information about dependencies, how to use the library, and other important details that are not covered here.

At a very high level this is what this library does:

1. Receives a Pillow image and other parameters
2. Subdivides the image into a number of row packages to calculate the CLAHE on.
3. Dispatches the row packages to ray for CLAHE calculation.
4. CLAHE is calculated for each package.
5. Resulting rows are re-assembled into a new image.
6. New image is returned.

## CLAHE

CLAHE is a [histogram equalization algorithm](https://en.wikipedia.org/wiki/Histogram_equalization). The advance the algorithm provides over other algorithms is that it localizes histogram equalization instead of equalizing the histogram for the image as a whole. In essence, the algorithm subdivides the image into different rectangular sections, and then equalizes the histogram independently for each section. This alone would typically end up with artifacts around each section, hence, another step CLAHE performs is that of normalizing the boundaries in other make the resulting image more harmonious. This is the original implementation of the algorithm by Karel Zuiderveld that appeared in "Graphics Gems IV", Academic Press, 1994. The algorithm chosen for this version is a bit different in that it creates a sliding window of a certain size that goes from the top of the image to the bottom. The histogram is then equalized row by row taking into consideration what rectangle such a row belongs to. You can find an implementation of this other version, in Java, [here](https://imagej.nih.gov/ij/plugins/clahe/CLAHE_.java).

The innovations of this algorithm over any of the two previously described versions are:

* Support for parallelism. Each image is subdivided into equally-sized groups of rows. The CLAHE algorithm is then run on each group independently. Reassembly of the new rows happens at the end.
* Support for color and grayscale images. Color images are converted into an HSV colorspace image. The V component is then used to equalize the histogram. The library supports 8 bpp and 16 bpp grayscale images.

## Requirements

These are the requirements the software was developed against:

1. The library shall perform the CLAHE algorithm on both color and grayscale images.
2. The library shall support input files in JPG, PNG, and TIFF format.
3. The library shall support grayscale images of an arbitrary color range.
4. The library shall support the passing of block size, slope, and bins to use by the CLAHE algorithm.
5. The library shall do its calculations "as fast as possible".

## Design

In this section I cover how the code supports the aforementioned requirements.

### 1, 2, 3

In order to partially accomplish requirements #1, #2, and #3, the library implements another library called Pillow. This library is well-known by Python developers and supports numerous input formats. Pillow lets users easily access pixel data that can be modified. It also lets users create new images with new or modified pixel data. The CLAHE algorithm itself supports arbitrary color ranges in one component, with the particularity that color images will always be converted into HSV to enjoy the V component for its histogram operations.

The main entry point for the code are the clahe_bw and clahe_color functions, that execute the CLAHE algorithm on grayscale and color images, respectively. The need to have two different functions stems from the fact that a user might want to treat a color image as grayscale. In essence, it's to provide flexibility for users.

### 1, 4

The clahe_bw and clahe_color functions support the block size, slope, and bins parameters via their signature have the following signatures:

    clahe_bw(image, blocksize, bins, slope, processes=0)
    clahe_color(image, blocksize, bins, slope, processes=0)

As an elaboration:

* image is the input Pillow image.
* blocksize is the size of the local region around a pixel for which the histogram is equalized.
* bins is the number of histogram bins used for histogram equalization.
* slope limits the contrast stretch in the intensity transfer function. 
* processes (optional) sets the number of processes to subdivide tasks across CPU cores.

Except for image, all of these parameters can be set to a 0 in case the user wants the library to pick values of its own.

The functions return a new Pillow image with the CLAHE pixel data.

### 5

The library has code optimizations that make the code look more C code than Python code (extensive use of loops, etc.), however, this was done after finding that numerical operations on arrays an lists were costly. I still blame my lack of Python knowledge for this anyway. It was also found that Python's round() function is slower than the round_positive() function currently in the code. Since this function is used frequently, the overhead became a small but still significant amount of time.

The largest increase in performance has been achieved with the use of parallelism in the code. It has been described above so I won't go into more details on this until later. At a very high level, I just subdivided the input image into equal chunks that were dispatched to different CLAHE processes implemented via the ray library. The new CLAHE image chunks are later reassembled into the image that is returned to the caller of the clahe_* methods.

## High-level flow

This section is provided in case the reader would like to understand more about how the code operates and possibly modify it for their own purposes. Note that most users' use of the library will be limited to calling the clahe_* methods.

1. User calls one of the clahe_* functions.
2. clahe_* initializes ray
3. clahe_* checks input parameters
4. clahe_* sets the bit depth to use
5. clahe_* creates a new image to copy new data to
6. clahe_* invokes do_clahe
    1. do_clahe creates the sub-image packages to be passed to processes
    2. for each package, do_clahe performs a 'remote' call to execute clahe_rows on each process. clahe rows is a function that executes the CLAHE algorithm from one row to another.
    3. do_clahe waits for each process to finish
    4. do_clahe assembles newly calculated rows into a 2D list
    5. do_clahe returns the 2D list to the calling clahe_* function
7. clahe_* places the 2D list into the new image
8. clahe_* returns the new image

## Additional functions

The CLAHE algorithm itself is contained in the clahe_rows and clahe_row functions. The former runs the CLAHE algorithm on an interval of rows while the latter runs the CLAHE algorithm in just one row. As one can check in the code, the clahe_rows function calls clahe_row.

The clahe_row function does the following:

1. Calculate the sub-image in which to calculate the histogram
2. Calculate the histogram
3. For each column (pixel in the row):
    1. Adjust histogram
    2. Clip histogram and redistribute clipped entries with clip_histogram
    3. Calculate CDF, CDF min, CDF max of the clipped histogram with calculate_cdf
    4. Calculate new pixel value as (cdf - cdfMin) / (cdfMax - cdfMin) * color_range
4. Save/return list of new pixel values

## Known Issues

* Minor: The code does not check the bins parameter to the clahe_* functions is smaller than the number of pixels in a block.
* Minor: While not a bug and already a considerable improvement over a serialized version of the algorithm. There must be avenues to improve performance either through technology (through a better understanding of Python), or via changes to the CLAHE algorithm itself. There is a fast version of the same algorithm that does not evaluate the intensity transfer function for each pixel independently but for a grid of adjacent boxes of the given block size only and interpolates for locations in between. This could prove substantially faster.

## Future work

* Performance enhancements (see above), including use of ray for work on remote computers.
* CLI and/or UI for the tool.
