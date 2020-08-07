# clahelib's Developer's Documentation

## Overview

A Python library that implements a parallelized version of the [Contrast Limited Adaptive Histogram Equalization (CLAHE)](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization) algorithm on image types supported by Pillow, including 16 bpp grayscale and color images. I would highly recommend prospective developers read the top-level README file, as it contains information about dependencies and other important details.

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

In this section we cover how the code supports the aforementioned requirements.

### The library shall perform the CLAHE algorithm on both color and grayscale images.
### The library shall support input files in JPG, PNG, and TIFF format.
### The library shall support grayscale images of an arbitrary color range.

In otder to accomplish this goal, the library implements another library called Pillow. This library is well-known by Python developers and supports numerous input formats.
