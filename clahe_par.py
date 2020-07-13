from PIL import Image
import numpy as np
import timeit
import collections
import multiprocessing as mp

def clahe_bw(image, blockRadius, bins, slope):

    blockRadius = int((blockRadius-1)/2)
    bins = int(bins-1)
    slope = float(slope)

    if image.mode != "L" or image.mode != "I:16":
        image = image.convert("L")

    color_range = 255
    if image.mode == "L":
        color_range = 255
    elif image.mode == "I;16":
        color_range = 65535
    
    pix = image.load()
    width, height = image.size
    new_image = image.copy()
    new_pix = new_image.load()

    dest_rows = clahe_rows(pix, color_range, 0, width, height, blockRadius, bins, slope)

    y = 0
    while y<height:
        x = 0
        while x<width:
            val = dest_rows[y][x]
            new_pix[x, y] = val
            x = x + 1
        y = y + 1

    return 0, new_image

def clahe_rows(pix, color_range, y_start, width, height, blockRadius, bins, slope):
    y = y_start
    dest_rows = []
    while y < height:
        dest_rows.append(clahe_row(pix, color_range, y, width, height, blockRadius, bins, slope))
        y = y + 1
    return dest_rows

def clahe_row(pix, color_range, y, width, height, blockRadius, bins, slope):
    yMin = max(0, y - blockRadius)
    yMax = min(height, y + blockRadius + 1)
    h = yMax - yMin

    xMin0 = max(0, -blockRadius)
    xMax0 = min(width - 1, blockRadius)

    hist = histogram(xMin0, xMax0, yMin, yMax, pix, color_range, bins)
    dest = []

    x = 0
    while x < width:
        v = roundPositive(pix[x, y] / color_range * bins)
        xMin = max(0, x - blockRadius)
        xMax = x + blockRadius + 1
        w = min(width, xMax) - xMin
        n = h * w

        limit = roundPositive(slope * n / bins)

        if xMin > 0:
            xMin1 = xMin - 1
            yi = yMin
            while yi < yMax:
                val = roundPositive(pix[xMin1, yi] / color_range * bins)
                hist[val] = hist[val] - 1
                yi = yi + 1

        if xMax <= width:
            xMax1 = xMax - 1
            yi = yMin
            while yi < yMax:
                val = roundPositive(pix[xMax1, yi] / color_range * bins)
                hist[val] = hist[val] + 1
                yi = yi + 1

        clippedHist = clip_histogram(hist, limit, bins)

        cdf, cdfMax, cdfMin = cdf_values(v, clippedHist, bins)
        col = roundPositive((cdf - cdfMin) / (cdfMax - cdfMin) * color_range)

        dest.append(col)
        x = x + 1
    
    return dest

def roundPositive(num):
    return int(num + 0.5)

def histogram(xMin, xMax, yMin, yMax, pixels, color_range, bins):
    hist = [0] * (bins + 1)
    yi = yMin
    while yi < yMax:
        xi = xMin
        while xi < xMax:
            val = roundPositive(pixels[xi, yi] / color_range * bins)
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
