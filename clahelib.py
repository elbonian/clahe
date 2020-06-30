from PIL import Image
import numpy as np
import timeit
import collections

def clahe(image, blockRadius, bins, slope):

    #EL1
    start_time = timeit.default_timer()

    dest_image = image.copy()
    dest_pix = dest_image.load()
    blockRadius = int((blockRadius-1)/2)
    bins = int(bins-1)
    slope = float(slope)
    box_x = box_y = 0
    box_width, box_height = image.size
    boxXMax = box_x + box_width
    boxYMax = box_y + box_height
    np_pix = np.array(image)
    pix = image.load()

    #EL1
    elapsed = timeit.default_timer() - start_time
    print("EL1: " + str(elapsed))

    y = box_y
    while y < boxYMax:
        yMin = max(0, y - blockRadius)
        yMax = min(box_height, y + blockRadius + 1)
        h = yMax - yMin

        xMin0 = max(0, box_x - blockRadius)
        xMax0 = min(box_width - 1, box_x + blockRadius)

        hist = histogram(xMin0, xMax0, yMin, yMax, pix, bins)

        #EL2
        start_time = timeit.default_timer()
        hist = histogram(xMin0, xMax0, yMin, yMax, pix, bins)
        #EL2
        elapsed = timeit.default_timer() - start_time
        print("EL2: " + str(elapsed))

        x = box_x
        #EL3
        start_time = timeit.default_timer()
        while x < boxXMax:
            v = roundPositive(pix[x,y] / 255 * bins)
            xMin = max(0, x - blockRadius)
            xMax = x + blockRadius + 1
            w = min(box_width, xMax) - xMin
            n = h * w

            limit = int(slope * n / bins + 0.5)

            if xMin > 0:
                xMin1 = xMin - 1
                yi = yMin
                while yi < yMax:
                    val = roundPositive(pix[xMin1,yi] / 255 * bins)
                    hist[val] = hist[val] - 1
                    yi = yi + 1
            
            if xMax <= box_width:
                xMax1 = xMax - 1
                yi = yMin
                while yi < yMax:
                    val = roundPositive(pix[xMax1,yi] / 255 * bins)
                    hist[val] = hist[val] + 1
                    yi = yi + 1
            
            clippedHist = hist.copy()
            clippedEntries = 0
            clippedEntriesBefore = 0
            #EL4
            start_time = timeit.default_timer()
            while True:
                clippedEntriesBefore = clippedEntries
                clippedEntries = 0
                i = 0
                while i <= bins:
                    d = clippedHist[i] - limit
                    if d>0:
                        clippedEntries = clippedEntries + d
                        clippedHist[i] = limit
                    i = i + 1
                
                d = int(clippedEntries / (bins + 1))
                m = int(clippedEntries % (bins + 1))
                i = 0
                while i <= bins:
                    clippedHist[i] = clippedHist[i] + d
                    i = i + 1
                
                if m!=0:
                    s = int(bins / m)
                    i = 0
                    while i <= bins:
                        clippedHist[i] = clippedHist[i] + 1
                        i = i + s
                if clippedEntries == clippedEntriesBefore:
                    break
            #EL4
            elapsed = timeit.default_timer() - start_time
            #print("EL4: " + str(elapsed))

            #EL5
            start_time = timeit.default_timer()
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
            col = roundPositive((cdf - cdfMin) / (cdfMax - cdfMin) * 255) 
            
            dest_pix[x, y] = col
            x = x + 1
            
            #EL5
            elapsed = timeit.default_timer() - start_time
            #print("EL5: " + str(elapsed))
        
        y = y + 1
        #EL3
        elapsed = timeit.default_timer() - start_time
        print("EL3: " + str(elapsed))

    #EL6
    start_time = timeit.default_timer()
    hMin = bins
    dest_image.save("images/output.png")
    #EL6
    elapsed = timeit.default_timer() - start_time
    print("EL6: " + str(elapsed))

def roundPositive(num):
    return int(num + 0.5)

def histogram(xMin0, xMax0, yMin, yMax, pix, bins):
    hist = [0] * (bins + 1)
    yi = yMin
    while yi < yMax:
        xi  = xMin0
        while xi < xMax0:
            val = roundPositive(pix[xi,yi] / 255 * bins)
            hist[val] = hist[val] + 1
            xi = xi + 1
        yi = yi + 1
    return hist