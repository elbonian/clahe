from PIL import Image

# Main clahe function. It will return an Image object when finished
# Implementation is based on "Graphics Gems IV", Academic Press, 1994
def clahe(image, num_x_regions, num_y_regions, num_of_bins, cliplimit):
    x_res = image.size[0]
    y_res = image.size[1]
    min_value = image.getextrema()[0]
    max_value = image.getextrema()[1]
    #TODO Complete code

    # Preliminary input checking
    # 1) image resolution on the X axis has to be a multiple of the number of X-axis regions
    if x_res % num_x_regions != 0:
        return -1
    # 2) image resolution on the Y axis has to be a multiple of the number of Y-axis regions
    if y_res % num_y_regions != 0:
        return -1
    # 3) number if regions can't be less than 2
    if num_y_regions < 2 or num_x_regions < 2:
        return -1
    # 4) if the number of bins passed is zero, let's assign a default 
    if num_of_bins == 0:
        num_of_bins = 128
    
    uiXSize = x_res / num_x_regions
    uiYSize = y_res / num_y_regions
    ulNrPixels = uiXSize * uiYSize

    if cliplimit>0:
        ulClipLimit = int(cliplimit * (uiXSize * uiYSize) / num_of_bins)
        if ulClipLimit < 1:
            ulClipLimit = 1
            # TODO: Finish this part?
    
    aLUT = make_lut(min_value, max_value, num_of_bins)

    print(aLUT)
    print(len(aLUT))


# To speed up histogram clipping, the input image [min_value,max_value] is scaled down to
# [, num_of_bins-1]. This function calculates the LUT.
def make_lut(min_value, max_value, num_of_bins):
    binsize = int(1 + (max_value - min_value) / num_of_bins)
    plut = []
    for i in range(min_value, max_value + 1):
        plut.append(int((i - min_value) / binsize))
    return plut