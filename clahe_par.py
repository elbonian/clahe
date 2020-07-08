from PIL import Image
import numpy as np
import timeit
import collections
import multiprocessing as mp
import ray



def clahe(image, blockRadius, bins, slope):

    blockRadius = int((blockRadius-1)/2)
    bins = int(bins-1)
    slope = float(slope)
    box_x = box_y = 0
    box_width, box_height = image.size
    boxXMax = box_x + box_width
    boxYMax = box_y + box_height
    np_pix = np.array(image)
    pix = image.load()
    new_image = image.copy()
    new_pix = new_image.load()

    y = box_y

    dest_rows = clahe_rows(pix, y, boxYMax, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax)
#    while y < boxYMax:
#        clahe_row(pix, y, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax)
#        y = y + 1

    y = 0
    while y<box_height:
        x = 0
        while x<box_width:
            val = dest_rows[y][x]
            new_pix[x, y] = val
            x = x + 1
        y = y + 1

    return new_image

def job1(pix, y, boxYMax, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax):
    pix = pix.load()
    clahe_rows(pix, y, boxYMax, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax)

def clahe_rows(pix, y_start, y_end, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax):
    y = y_start
    dest_rows = []
    while y < y_end:
        dest_rows.append(clahe_row(pix, y, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax))
        y = y + 1
    return dest_rows

def roundPositive(num):
    return int(num + 0.5)

def histogram(xMin, xMax, yMin, yMax, pixels, bins):
    hist = [0] * (bins + 1)
    yi = yMin
    while yi < yMax:
        xi = xMin
        while xi < xMax:
            val = roundPositive(pixels[xi, yi] / 255 * bins)
            hist[val] = hist[val] + 1
            xi = xi + 1
        yi = yi + 1
    return hist

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


def cdf_values(v, clippedHist, bins):
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

def clahe_row(pix, y, blockRadius, bins, slope, box_width, box_height, box_x, boxXMax):
    yMin = max(0, y - blockRadius)
    yMax = min(box_height, y + blockRadius + 1)
    h = yMax - yMin

    xMin0 = max(0, box_x - blockRadius)
    xMax0 = min(box_width - 1, box_x + blockRadius)

    hist = histogram(xMin0, xMax0, yMin, yMax, pix, bins)
    dest = []

    x = box_x
    while x < boxXMax:
        v = roundPositive(pix[x, y] / 255 * bins)
        xMin = max(0, x - blockRadius)
        xMax = x + blockRadius + 1
        w = min(box_width, xMax) - xMin
        n = h * w

        limit = int(slope * n / bins + 0.5)

        if xMin > 0:
            xMin1 = xMin - 1
            yi = yMin
            while yi < yMax:
                val = roundPositive(pix[xMin1, yi] / 255 * bins)
                hist[val] = hist[val] - 1
                yi = yi + 1

        if xMax <= box_width:
            xMax1 = xMax - 1
            yi = yMin
            while yi < yMax:
                val = roundPositive(pix[xMax1, yi] / 255 * bins)
                hist[val] = hist[val] + 1
                yi = yi + 1

        clippedHist = clip_histogram(hist, limit, bins)

        cdf, cdfMax, cdfMin = cdf_values(v, clippedHist, bins)
        col = roundPositive((cdf - cdfMin) / (cdfMax - cdfMin) * 255)

        dest.append(col)
        x = x + 1
    
    return dest
