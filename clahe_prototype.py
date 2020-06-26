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
#    else:
#        ulClipLimit = 1 << 14
    
    aLUT = make_lut(min_value, max_value, num_of_bins)

    print(aLUT)
    print(len(aLUT))

    channel_data = list(image.getdata())

    uiY = 0
    pImPos = 0
    while uiY < uiNrY:
        uiX = 0
        while uiX < uiNrX:
            #TODO add increment to pulHist
            pulHist = make_histogram(channel_data, pImPos, x_res, uiXSize, uiYSize, num_of_bins, aLUT)
            print(pulHist)
            pulHist = clip_histogram(pulHist, num_of_bins, ulClipLimit)
            map_histogram(pulHist, min_value, max_value, num_of_bins, ulNrPixels)
            uiX = uiX + 1
            pImPos = pImPos + uiXSize
        uiY = uiY + 1
        pImPos = pImPos + (uiYSize - 1) * x_res
    
    print(pulHist)

    uiY = pImPos = uiSubY = uiSubX = uiYU = uiYB = uiXL = uiXR = 0
    while uiY <= uiNrY:
        if uiY == 0:
            uiSubY = int(uiYSize) >> 1
            uiYU = uiNrY - 1
            uiYB = uiYU
        else:
            if uiY == uiNrY:
                uiSubY = int(uiYSize) >> 1
                uiYU = uiNrY - 1
                uiYB = uiYU
            else:
                uiSubY = uiYSize
                uiYU = uiYU - 1
                uiYB = uiYU + 1
        uiX = 0
        while uiX <= uiNrX:
            if uiX == 0:
                uiSubX = int(uiXSize) >> 1
                uiXL = 0
                uiXR = 0
            else:
                if uiX == uiNrX:
                    uiSubX = int(uiXSize) >> 1
                    uiXL = uiNrX - 1
                    uiXR = uiXL
                else:
                    uiSubX = uiXSize
                    uiXL = uiX - 1
                    uiXR = uiXL + 1
            pulLUPos = num_of_bins * (uiYU * uiNrX + uiXL)
            pulRUPos = num_of_bins * (uiYU * uiNrX + uiXR)
            pulLBPos = num_of_bins * (uiYB * uiNrX + uiXL)
            pulRBPos = num_of_bins * (uiYB * uiNrX + uiXR)
            interpolate(channel_data, pulHist, x_res, pulLUPos, pulRUPos, pulLBPos, pulRBPos, uiSubX, uiSubY, aLUT)
            pImPos = pImPos + uiSubX
            uiX = uiX + 1
        pImPos = pImPos + (uiSubY - 1) * x_res
        uiY = uiY + 1
        #finish return
        


# To speed up histogram clipping, the input image [min_value,max_value] is scaled down to
# [, num_of_bins-1]. This function calculates the LUT.
def make_lut(min_value, max_value, num_of_bins):
    binsize = int(1 + (max_value - min_value) / num_of_bins)
    plut = []
    for i in range(min_value, max_value + 1):
        plut.append(int((i - min_value) / binsize))
    return plut

def make_histogram(channel_data, pos, uiXRes, uiSizeX, uiSizeY, uiNrGreylevels, pLookupTable):
    histogram = [0] * uiNrGreylevels #TODO fix this, not entirely correct
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

def interpolate(pImage, pulHist, uiXRes, pulMapLUPos, pulMapRUPos, pulMapLBPos, pulMapRBPos, uiXSize, uiYSize, pLUT):
    uiIncr = uiXRes - uiXSize
    uiXCoef = uiYCoef = uiXInvCoef = uiYInvCoef = uiShift = GreyValue = pImagePos = 0
    uiNum = uiXSize * uiYSize
    if uiNum & (uiNum - 1):
        uiYCoef = 0
        uiYInvCoef = uiYSize
        while uiYCoef < uiYSize:
            uiXCoef = 0
            uiXInvCoef = uiXSize
            while uiXCoef < uiXSize:
                GreyValue = pLUT[pImagePos]
                pImage[pImagePos] = int((uiYInvCoef * (uiXInvCoef * pulHist[GreyValue+pulMapLUPos] + uiXCoef * pulHist[GreyValue + pulMapRUPos])
                + uiYCoef * (uiXInvCoef * pulHist[GreyValue + pulMapLBPos] + uiXCoef * pulHist[GreyValue + pulMapRBPos])) / uiNum)
                pImagePos = pImagePos + 1
                uiXCoef = uiXCoef + 1
                uiXInvCoef = uiXInvCoef - 1
            uiYCoef = uiYCoef + 1
            uiYInvCoef = uiYInvCoef - 1
            pImagePos = pImagePos + uiIncr
    else:
        #uiNum = uiNum >> 1
        while uiNum:
            uiNum = uiNum >> 1
            uiShift = uiShift + 1
        uiYCoef = 0
        uiYInvCoef = uiYSize
        while uiYCoef < uiYSize:
            uiXCoef = 0
            uiXInvCoef = uiXSize
            while uiXCoef < uiXSize:
                GreyValue = pLUT[pImagePos]
                pImage[pImagePos] = int((uiYInvCoef * (uiXInvCoef * pulHist[GreyValue+pulMapLUPos] + uiXCoef * pulHist[GreyValue + pulMapRUPos])
                + uiYCoef * (uiXInvCoef * pulHist[GreyValue + pulMapLBPos] + uiXCoef * pulHist[GreyValue + pulMapRBPos])) >> uiShift)
                uiXCoef = uiXCoef + 1
                uiXInvCoef = uiXInvCoef - 1
            uiYCoef = uiYCoef + 1
            uiYInvCoef = uiYInvCoef - 1
            pImagePos = pImagePos + uiIncr
    return pImage


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