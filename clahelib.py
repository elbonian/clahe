from PIL import Image
import math
import multiprocessing
import ray

"""
clahe_bw() function calculates CLAHE in black and white.
    It supports 8 bpp and 16 bpp grayscale images.
    If image passed is not of the supported type, it will be converted to 8 bpp grayscale.

image       is the input Pillow Image
blocksize   is the size of the local region around a pixel for which the histogram is equalized.
            This size should be larger than the size of features to be preserved.
bins        is the number of histogram bins used for histogram equalization.
            The number of histogram bins should be smaller than the number of pixels in a block (blocksize^2).
slope       limits the contrast stretch in the intensity transfer function.
processes   sets the number of processes to subdivide tasks across CPU cores.
            A value of 1 is essentially a serial version of the algorithm.
            Not setting this value or setting it to 0 will make the algorithm set a value of its choosing.
"""
def clahe_bw(image, blocksize, bins, slope, processes=0):

    # We initialize ray here, the parallelization library.
    # The parameter passed to ray.init() makes this function do nothing
    # if ray has already been initialized.
    ray.init(ignore_reinit_error=True)

    # Check processes input
    processes = get_processnumber(processes)

    # Turn block size into internal block radius
    blockradius = get_blockradius(image, blocksize)
    slope = get_slope(slope)

    # Convert image to 8 bpp grayscale if needed
    if image.mode != "L" or image.mode != "I:16":
        image = image.convert("L")

    # Set color ranges per image mode
    color_range = 255
    if image.mode == "I;16":
        color_range = 65535
    
    bins = get_bins(color_range, bins)

    # Load original image, destination, and size.
    new_image = image.copy()
    new_pix = new_image.load()

    dest_rows = do_clahe(image, color_range, blockradius, bins, slope, processes)

    # Place the CLAHE pixel values into the new image
    width, height = image.size
    y = 0
    while y<height:
        x = 0
        while x<width:
            val = dest_rows[y][x]
            new_pix[x, y] = val
            x = x + 1
        y = y + 1

    return new_image

"""
clahe_color() function calculates CLAHE in color.
    Images passed are converted to the HSV color space internally but returned in original color space.

image       is the input Pillow Image
blocksize   is the size of the local region around a pixel for which the histogram is equalized.
            This size should be larger than the size of features to be preserved.
bins        is the number of histogram bins used for histogram equalization.
            The number of histogram bins should be smaller than the number of pixels in a block (blocksize^2).
slope       limits the contrast stretch in the intensity transfer function.
processes   sets the number of processes to subdivide tasks across CPU cores.
            A value of 1 is essentially a serial version of the algorithm.
            Not setting this value or setting it to 0 will make the algorithm set a value of its choosing.
"""
def clahe_color(image, blocksize, bins, slope, processes=0):

    # We initialize ray here, the parallelization library.
    # The parameter passed to ray.init() makes this function do nothing
    # if ray has already been initialized.
    ray.init(ignore_reinit_error=True)

    # Check processes input
    processes = get_processnumber(processes)

    # Turn block size into internal block radius
    blockradius = get_blockradius(image, blocksize)
    slope = get_slope(slope)
    
    # Need to save original mode to re-convert before returning image
    orig_mode = image.mode

    # Need intensity values rather than color values, so HSV is a good fit
    image = image.convert("HSV")
    color_range = 255
    
    bins = get_bins(color_range, bins)

    # Load original image, destination, and sizes
    new_image = image.copy()
    new_pix = new_image.load()

    # Execute the CLAHE algorithm
    dest_rows = do_clahe(image, color_range, blockradius, bins, slope, processes)

    # Place the CLAHE pixel values into the new image
    width, height = image.size
    y = 0
    while y<height:
        x = 0
        while x<width:
            val = dest_rows[y][x]
            # Need to build a tuple given HSV has 3 components
            new_pix[x, y] = (new_pix[x,y][0], new_pix[x,y][1], val)
            x = x + 1
        y = y + 1

    # Return image in the original mode
    new_image = new_image.convert(orig_mode)

    return new_image

"""
The 3 following functions check the blocksize, bins, slope, and processes inputs and react accordingly.
One key function for the functions is to auto-set the values if the user made a mistake or decides 
to let the library choose values (if they pass a 0 value in any parameter).
"""
def get_blockradius(image, blocksize):
    if blocksize < 5:
        width, height = image.size
        # Calculate a possibly good blocksize
        new_blocksize = int(min(width, height)/4)
        return int((new_blocksize-1)/2)
    else:
        return int((blocksize-1)/2)

def get_bins(color_range, bins):
    # Auto-set bins
    if bins <= 0:
        bins = 256
    # and check if auto-set or user passed value is not over range
    if bins > color_range:
        return color_range
    
    return int(bins-1)

def get_slope(slope):
    if slope < 1:
        # Auto-set to 2.0
        return 2.0
    else:
        return float(slope)

def get_processnumber(processes):
    # Auto-set the number of processes needed, if requested.
    if processes == 0:
        processes = multiprocessing.cpu_count()-1
    # And check we are not using 0 after all after the previous assignment
    if processes == 0:
        processes = 1
    return processes

"""
do_clahe() executes the CLAHE algorithm on an image in a parallelized manner.
    It packages work so it can be executed by the number of processes passed as parameter.
    This function is heaviliy commented to understand the use of ray.
"""
def do_clahe(image, color_range, blockradius, bins, slope, processes):
    
    # Start by calculating the increment in rows for each successive work package
    height = image.size[1]
    # Packages will be equal in size
    height_increment = round_positive(height/processes)

    # We start with row 0
    height_pointer = 0

    # This variable captures the results from every job
    result_rows = []

    # Package creation and dispatching to processes happens here
    while height_pointer < height:

        # This is needed to ensure we don't create a last package that calculates
        # the CLAHE outside of image boundaries (at the bottom of the image).
        if height_pointer+height_increment > height:
            stop_row = height
        # In the general case, we just package based on the row from where
        # we left off plus the height offset per package.
        else:
            stop_row = height_pointer+height_increment

        # We execute a process with its work package
        result_rows.append(clahe_rows.remote(image, color_range, height_pointer, stop_row, blockradius, bins, slope))
        # We keep going
        height_pointer = height_pointer + height_increment

    # This variable contains the CLAHE image values
    # Note that this variable is built from results from each process 
    dest_rows = []
    # For each result from each process...
    for result in result_rows:
        # We get the CLAHE rows calculated
        # The ray.get() method retrieves data and does a join() BTW
        intermediate_row_result = ray.get(result)
        # Merge the results into dest_rows
        length = len(intermediate_row_result)
        i = 0
        while i < length:
            dest_rows.append(intermediate_row_result[i])
            i = i + 1
    return dest_rows

"""
clahe_rows() executes the CLAHE algorithm on chosen rows.
    This function is a 'job' for processes when parallelizing.
    Of particular interest is the @ray.remote annotation.
    It denotes this function can be parallelized by ray.
"""
@ray.remote
def clahe_rows(image, color_range, start_row, stop_row, blockradius, bins, slope):
    
    width, height = image.size
    pix = image.load()
    
    y = start_row
    dest_rows = []
    while y < stop_row:
        dest_rows.append(clahe_row(pix, color_range, y, width, height, blockradius, bins, slope))
        y = y + 1
    return dest_rows

"""
clahe_row() executes the CLAHE algorithm on a single row. 
"""
def clahe_row(pix, color_range, y, width, height, blockradius, bins, slope):
    yMin = max(0, y - blockradius)
    yMax = min(height, y + blockradius + 1)
    h = yMax - yMin

    xMin0 = max(0, -blockradius)
    xMax0 = min(width - 1, blockradius)

    hist = calculate_histogram(xMin0, xMax0, yMin, yMax, pix, color_range, bins)
    dest = []

    x = 0
    while x < width:
        v = round_positive(get_pix_value(pix[x, y]) / color_range * bins)
        xMin = max(0, x - blockradius)
        xMax = x + blockradius + 1
        w = min(width, xMax) - xMin
        n = h * w

        limit = round_positive(slope * n / bins)

        # Remove left behind values from histogram.
        if xMin > 0:
            xMin1 = xMin - 1
            yi = yMin
            while yi < yMax:
                val = round_positive(get_pix_value(pix[xMin1, yi]) / color_range * bins)
                hist[val] = hist[val] - 1
                yi = yi + 1

        # Add newly included values to histogram.
        if xMax <= width:
            xMax1 = xMax - 1
            yi = yMin
            while yi < yMax:
                val = round_positive(get_pix_value(pix[xMax1, yi]) / color_range * bins)
                hist[val] = hist[val] + 1
                yi = yi + 1

        clippedHist = clip_histogram(hist, limit, bins)

        cdf, cdfMax, cdfMin = calculate_cdf(v, clippedHist, bins)
        col = round_positive((cdf - cdfMin) / (cdfMax - cdfMin) * color_range)

        dest.append(col)
        x = x + 1
    
    return dest

"""
round_positive() rounds numbers. It is faster than Python's round().
https://stackoverflow.com/questions/44920655/python-round-too-slow-faster-way-to-reduce-precision
"""
def round_positive(num):
    return int(num + 0.5)

"""
get_pix_value() selects the intensity value of a HSV tuple passed as parameter.
    It returns the passed value if the same is not a tuple. 
"""
def get_pix_value(v):
    if type(v) is tuple:
        return v[2]
    else:
        return v

"""
calculate_histogram() calculates the histogram around a region defined by the current row and the block radius.
"""
def calculate_histogram(xMin, xMax, yMin, yMax, pixels, color_range, bins):
    hist = [0] * (bins + 1)
    yi = yMin
    while yi < yMax:
        xi = xMin
        while xi < xMax:
            val = round_positive(get_pix_value(pixels[xi, yi]) / color_range * bins)
            hist[val] = hist[val] + 1
            xi = xi + 1
        yi = yi + 1
    return hist

"""
clip_histogram() clips the histogram and redistributes clipped entries.
"""
def clip_histogram(hist, limit, bins):
    clippedHist = hist.copy()
    clippedEntries = 0
    clippedEntriesBefore = 0
    while True:
        clippedEntriesBefore = clippedEntries
        clippedEntries = 0
        i = 0
        while i <= bins:
            d = clippedHist[i] - limit
            if d > 0:
                clippedEntries = clippedEntries + d
                clippedHist[i] = limit
            i = i + 1

        d = int(clippedEntries / (bins + 1))
        m = int(clippedEntries % (bins + 1))
        i = 0
        while i <= bins:
            clippedHist[i] = clippedHist[i] + d
            i = i + 1

        if m != 0:
            s = int(bins / m)
            i = 0
            while i <= bins:
                clippedHist[i] = clippedHist[i] + 1
                i = i + s
        if clippedEntries == clippedEntriesBefore:
            break
    
    return clippedHist

"""
calculate_cdf() builds the cdf of the clipped histogram.
"""
def calculate_cdf(v, clippedHist, bins):
    hMin = bins
    
    i = 0
    while i < hMin:
        if clippedHist[i] != 0:
            hMin = i
        i = i + 1

    cdf = 0
    i = hMin
    while i <= v:
        cdf = cdf + clippedHist[i]
        i = i + 1
            
    cdfMax = cdf
    i = v + 1
    while i <= bins:
        cdfMax = cdfMax + clippedHist[i]
        i = i + 1
            
    cdfMin = clippedHist[hMin]

    return cdf, cdfMax, cdfMin
