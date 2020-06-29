from PIL import Image

def clahe(image, blockRadius, bins, slope):
    dest_image = image.copy()
    dest_pix = dest_image.load()
    blockRadius = int(blockRadius)
    bins = int(bins-1)
    slope = float(slope)
    box_x = box_y = 0
    box_width, box_height = image.size
    boxXMax = box_x + box_width
    boxYMax = box_y + box_height
    pix = image.load()

    y = box_y
    while y < boxYMax:
        print(y, "of", boxYMax)
        yMin = max(0, y - blockRadius)
        yMax = min(box_height, y + blockRadius + 1)
        h = yMax - yMin

        xMin0 = max(0, box_x - blockRadius)
        xMax0 = min(box_width - 1, box_x + blockRadius)

        hist = [0] * (bins + 1)
        yi = yMin
        while yi < yMax:
            xi  = xMin0
            while xi < xMax0:
                val = round(pix[xi, yi] / 255 * bins)
                hist[val] = hist[val] + 1
                xi = xi + 1
            yi = yi + 1
        
        x = box_x
        while x < boxXMax:
            v = round(pix[x, y] / 255 * bins)
            xMin = max(0, x - blockRadius)
            xMax = x + blockRadius + 1
            w = min(box_width, xMax) - xMin
            n = h * w

            limit = int(slope * n / bins + 0.5)

            if xMin > 0:
                xMin1 = xMin - 1
                yi = yMin
                while yi < yMax:
                    val = round(pix[xMin1, yi] / 255 * bins)
                    hist[val] = hist[val] - 1
                    yi = yi + 1
            
            if xMax <= box_width:
                xMax1 = xMax - 1
                yi = yMin
                while yi < yMax:
                    val = round(pix[xMax1, yi] / 255 * bins)
                    hist[val] = hist[val] + 1
                    yi = yi + 1
            
            clippedHist = hist.copy()
            clippedEntries = 0
            clippedEntriesBefore = 0
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

            hMin = bins
            '''
            i = 0
            while i < hMin:
                if clippedHist[i] != 0:
                    hMin = i
                i = i + 1
            '''
            # CH using list in instead
            if 0 not in clippedHist[0:hMin]: # slice
                hMin = 1

            # CH: using numpy instead
            import numpy as np
            clippedHist_a = np.array(clippedHist)
            ss = clippedHist_a[0:hMin] # subset
            if 0 not in ss:
                hMin = 1

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
            col = round((cdf - cdfMin) / (cdfMax - cdfMin) * 255) # use build-in round()!
            
            dest_pix[x, y] = col
            x = x + 1
        
        y = y + 1

    print()
    dest_image.save("images/output.png")

