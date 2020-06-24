from PIL import Image

# Main clahe function. It will return an Image object when finished
# Implementation is based on "Graphics Gems IV", Academic Press, 1994
def clahe(image, uiNrX, uiNrY, num_of_bins, cliplimit):
    x_res = image.size[0]
    y_res = image.size[1]
    min_value = image.getextrema()[0]
    max_value = image.getextrema()[1]
    #TODO Complete code

    # Preliminary input checking
    # 1) image resolution on the X axis has to be a multiple of the number of X-axis regions
    if x_res % uiNrX != 0:
        return -1
    # 2) image resolution on the Y axis has to be a multiple of the number of Y-axis regions
    if y_res % uiNrY != 0:
        return -1
    # 3) number if regions can't be less than 2
    if uiNrY < 2 or uiNrX < 2:
        return -1
    # 4) if the number of bins passed is zero, let's assign a default 
    if num_of_bins == 0:
        num_of_bins = 128
    
    uiXSize = x_res / uiNrX
    uiYSize = y_res / uiNrY
    ulNrPixels = uiXSize * uiYSize

    if cliplimit>0:
        ulClipLimit = int(cliplimit * (uiXSize * uiYSize) / num_of_bins)
        if ulClipLimit < 1:
            ulClipLimit = 1
            # TODO: Finish this part?
    
    aLUT = make_lut(min_value, max_value, num_of_bins)

    print(aLUT)
    print(len(aLUT))

    channel_data = list(image.getdata())

    uiY = 0
    pImPos = 0
    while uiY < uiNrY:
        uiX = 0
        while uiX < uiNrX:
            pulHist = make_histogram(channel_data, pImPos, x_res, uiXSize, uiYSize, num_of_bins, aLUT)
            clip_histogram(pulHist, num_of_bins, ulClipLimit)
            map_histogram(pulHist, min_value, max_value, num_of_bins, ulNrPixels)
            uiX = uiX + 1
            pImPos = pImPos + uiXSize
        uiY = uiY + 1
        pImPos = pImPos + (uiYSize - 1) * x_res
    # TODO implement interpolation

# To speed up histogram clipping, the input image [min_value,max_value] is scaled down to
# [, num_of_bins-1]. This function calculates the LUT.
def make_lut(min_value, max_value, num_of_bins):
    binsize = int(1 + (max_value - min_value) / num_of_bins)
    plut = []
    for i in range(min_value, max_value + 1):
        plut.append(int((i - min_value) / binsize))
    return plut

def make_histogram(channel_data, pos, uiXRes, uiSizeX, uiSizeY, uiNrGreylevels, pLookupTable):
    histogram = [0] * uiNrGreylevels
    i = 0
    while i < uiSizeY:
        imagePointer = uiSizeX
        while pos < imagePointer:
            pixel_value = channel_data[pos]
            lut_value = pLookupTable[pixel_value]
            histogram[lut_value] = histogram[lut_value] + 1
            pos = pos + 1
        imagePointer = imagePointer + uiXRes
        pos = int(pos - uiSizeX)
        i = i + 1
    return histogram

def clip_histogram(pulHistogram, uiNrGreylevels, ulClipLimit):
    ulNrExcess = 0
    lBinExcess = 0
    
    i = 0
    while i < uiNrGreylevels:
        lBinExcess = int(pulHistogram[i]) - int(ulClipLimit)
        if lBinExcess > 0:
            ulNrExcess = ulNrExcess + lBinExcess
        i = i + 1
    
    ulBinIncr = int(ulNrExcess / uiNrGreylevels)
    ulUpper = ulClipLimit - ulBinIncr

    i = 0
    while i < uiNrGreylevels:
        if pulHistogram[i] > ulClipLimit:
            pulHistogram[i] = ulClipLimit
        else:
            if pulHistogram[i] > ulUpper:
                ulNrExcess = ulNrExcess - pulHistogram[i] - ulUpper
                pulHistogram[i] = ulClipLimit
            else:
                ulNrExcess = ulNrExcess - ulBinIncr
                pulHistogram[i] = pulHistogram[i] + ulBinIncr
        i = i + 1
    
    pulEndPos = 0
    while ulNrExcess:
        pulEndPos = uiNrGreylevels
        pulHistoPos = 0
        while ulNrExcess and pulHistoPos < pulEndPos:
            ulStepSize = int(uiNrGreylevels / ulNrExcess)
            if ulStepSize < 1:
                ulStepSize = 1
            pulBinPos = pulHistoPos
            while pulBinPos < pulEndPos and ulNrExcess:
                if pulHistogram[pulBinPos] < ulClipLimit:
                    pulHistogram[pulBinPos] = pulHistogram[pulBinPos] - 1
                    ulNrExcess = ulNrExcess - 1
                pulBinPos = pulBinPos + ulStepSize
            pulHistoPos = pulHistoPos + 1
    
    return pulHistogram

def map_histogram(pulHistogram, Min, Max, uiNrGreylevels, ulNrOfPixels):
    ulSum = 0
    fScale = (Max - Min)/ulNrOfPixels

    i = 0
    while i < uiNrGreylevels:
        ulSum = ulSum + pulHistogram[i]
        pulHistogram[i] = int(Min + ulSum * fScale)
        if pulHistogram[i] > Max:
            pulHistogram[i] = Max
        i = i + 1
    
    return pulHistogram