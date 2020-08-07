# clahelib's Developer's Documentation

## Overview

A Python library that implements a parallelized version of the [Contrast Limited Adaptive Histogram Equalization (CLAHE)](https://en.wikipedia.org/wiki/Adaptive_histogram_equalization) algorithm on image types supported by Pillow, including 16 bpp grayscale and color images. I would highly recommend prospective developers read the top-level README file, as it contains information about dependencies and other important details.

At a very high level this is what it does:

1. Receives a Pillow image and other parameters
2. Subdivides the image into a number of row packages to calculate the CLAHE on.
3. Dispatches the row packages to ray for CLAHE calculation.
4. CLAHE is calculated for each package.
5. Resulting rows are re-assembled into a new image.
6. New image is returned.

## CLAHE

CLAHE is a [histogram equalization algorithm](https://en.wikipedia.org/wiki/Histogram_equalization). The advance the algorithm provides over other algorithms is that it localizes histogram equalization instead of equalizing the histogram for the image as a whole. In essence, the algorithm subdivides the image into different sections, and then equalizes the histogram independently for each section. This alone would typically end up with artifacts around each section, hence, another step CLAHE performs is that of normalizing the boundaries in other make the resulting image more harmonious.

There are different CLAHE implementations of the CLAHE algorithm. The original one from by Karel Zuiderveld that appeared in "Graphics Gems IV", Academic Press, 1994
