from PIL import Image

def clahe(image, blocRadius, bins, slope):
    blockRadius = int(blockRadius)
    bins = int(bins)
    slope = float(slope)
    box_x = box_y = 0
    box_width = image.size[0]
    box_height = image.size[1]
    boxXMax = box_x + box_width
    boxYMax = box_y + box_height

    y = box_y
    while y < boxYMax:
        yMin = max(0, y - blockRadius)
        yMax = min(box_height, y + blockRadius + 1)
        h = yMax - yMin

        xMin0 = max(0, box_x - blockRadius)
        xMax0 = max(box_width - 1, box_x + blockRadius)

        hist = [0] * (bins + 1)
        yi = yMin
        while yi < yMax:
            xi  = xMin0
            while xi < xMax0:
                v = int(image.getpixel(xi, yi) / 255 * bins)
                hist[v] = hist[v] + 1
                xi = xi + 1
            yi = yi + 1
        
        x = box_x
        while x < boxXMax:
            v = int(image.getpixel(xi, yi) / 255 * bins)
            xMin = max(0, x - blockRadius)
            xMax = x + blockRadius + 1
            w = min(box_width, xMax) - 1
            n = h * w

            limit = int(slope * n / bins + 0.5)

            if xMin > 0:
                xMin1 = xMin - 1
                yi = yMin
                while yi < yMax:
                    v = int(image.getpixel(xMin1, yi) / 255 * bins)
                    hist[v] = hist[v] - 1
                    yi = yi + 1
            
            if xMax <= box_width:
                xMax1 = xMax - 1
                yi = yMin
                while yi < yMax:
                    v = int(image.getpixel(xMax1, yi) / 255 * bins)
                    hist[v] = hist[v] + 1
                    yi = yi + 1
            
            #shallow copy suffices given we are dealing with ints
            clippedHist = hist.copy()
            clippedEntries = clippedEntriesBefore = 0
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
                
                d = clippedEntries / (bins + 1)
                m = clippedEntries % (bins + 1)
                i = 0
                while i <= bins:
                    clippedHist[i] = clippedHist[i] + d
                    i = i + 1
                
                if m!=0:
                    s = bins / m
                    i = 0
                    while i <= bins:
                        clippedHist[i] = clippedHist[i] + 1
                        i = i + s
                if clippedEntries != clippedEntriesBefore:
                    break
            
            #build cdf

            
            x = x + 1
        
        
        
        
        y = y + 1