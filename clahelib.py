from PIL import Image

"""
clahe_bw() function calculates CLAHE in black and white.
    It supports 8 bpp and 16 bpp grayscale images.
    If image passed is not of the supported type, it will be converted to 8 bpp grayscale.

image       is a Pillow Image
blockSize   is the size of the local region around a pixel for which the histogram is equalized.
            This size should be larger than the size of features to be preserved.
bins        is the number of histogram bins used for histogram equalization.
             The number of histogram bins should be smaller than the number of pixels in a block.
slope       limits the contrast stretch in the intensity transfer function.
"""
def clahe_bw(image, blockSize, bins, slope):

    # Turn block size into internal block radius
    blockRadius = int((blockSize-1)/2)
    bins = int(bins-1)
    slope = float(slope)

    # Convert image to 8 bpp grayscale if needed
    if image.mode != "L" or image.mode != "I:16":
        image = image.convert("L")

    # Set color ranges per image mode
    color_range = 255
    if image.mode == "I;16":
        color_range = 65535
    
    # Load original image, destination, and size
    pix = image.load()
    width, height = image.size
    new_image = image.copy()
    new_pix = new_image.load()

    # Execute CLAHE on all image rows
    dest_rows = clahe_rows(pix, color_range, 0, width, height, blockRadius, bins, slope)

    # Place the CLAHE pixel values into the new image
    y = 0
    while y<height:
        x = 0
        while x<width:
            val = dest_rows[y][x]
            new_pix[x, y] = val
            x = x + 1
        y = y + 1

    return 0, new_image

"""
clahe_color() function calculates CLAHE in color.
    Images passed are converted to the HSV color space internally.
    Parameters are the same as for black and white version above.
"""
def clahe_color(image, blockSize, bins, slope):

    # Turn block size into internal block radius
    blockRadius = int((blockSize-1)/2)
    bins = int(bins-1)
    slope = float(slope)
    
    # Need to save original mode to re-convert before returning image
    orig_mode = image.mode

    # Need intensity values rather than color values, so HSV is a good fit
    image = image.convert("HSV")
    color_range = 255
    
    # Load original image, destination, and sizes
    pix = image.load()
    width, height = image.size
    new_image = image.copy()
    new_pix = new_image.load()

    # Execute CLAHE on all image rows
    dest_rows = clahe_rows(pix, color_range, 0, width, height, blockRadius, bins, slope)

    # Place the CLAHE pixel values into the new image
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

    return 0, new_image

#
# CH: using a worker Pool for multiprocessing
#

from multiprocessing import Pool, freeze_support, current_process
#import dill as pickle
"""
clahe_rows() executes the CLAHE algorithm on all rows.
    It is a candidate for parallelization given no data dependency among clahe_row calls!
"""
def call_clahe_row(row_tuple):
    print(current_process()) # id for current process
    print(row_tuple) # "args" for clahe_row()
    #r =  clahe_row(*row_tuple) # * means unroll args from tuple and pretend they are normal args
    return 123 # would return r


def clahe_rows(pix, color_range, y_start, width, height, blockRadius, bins, slope):
    y = y_start
    row_list = []
    while y < height:
        #dest_rows.append(clahe_row(pix, color_range, y, width, height, blockRadius, bins, slope))
        # make a tuple from the args that the functions need to get
        row_list.append((pix, color_range, y, width, height, blockRadius, bins, slope)) 
        y = y + 1

    pool = Pool(processes=None, maxtasksperchild=1) # processes=None means use all available cores

    try:
        # call_clahe_row is called with its args in form of a tuple
        dest_rows = pool.map(call_clahe_row, row_list)
    except Exception as e:
        print(e)
    else:
        pool.close()
        pool.terminate()

    #print(dest_rows) # contains list of results
    return dest_rows

# CH MAIN
if __name__ == '__main__':
    freeze_support() # needed on Windows
    dest_list = clahe_rows(1,2,3,4,5,6,7,8) # will spawn 2 processes (5-3) for processing and get a list of 2 processed objects
    print(dest_list)




"""
clahe_row() executes the CLAHE algorithm on a single row. 
"""
def clahe_row(pix, color_range, y, width, height, blockRadius, bins, slope):
    yMin = max(0, y - blockRadius)
    yMax = min(height, y + blockRadius + 1)
    h = yMax - yMin

    xMin0 = max(0, -blockRadius)
    xMax0 = min(width - 1, blockRadius)

    hist = calculate_histogram(xMin0, xMax0, yMin, yMax, pix, color_range, bins)
    dest = []

    x = 0
    while x < width:
        v = round_positive(get_pix_value(pix[x, y]) / color_range * bins)
        xMin = max(0, x - blockRadius)
        xMax = x + blockRadius + 1
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
