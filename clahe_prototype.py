from PIL import Image

im = Image.open("images/cell_gray16.tif")
clahe(im, 128, 2.0)

# Main clahe function. It will return an Image object when finished
# Implementation is based on "Graphics Gems IV", Academic Press, 1994
def clahe(image, number_of_bins, cliplimit):
    x_res = image.size[0]
    y_res = image.size[1]
    min_value = image.getextrema()[0]
    max_value = image.getextrema()[1]
    #TODO Complete code

# To speed up histogram clipping, the input image [min_value,max_value] is scaled down to
# [0,number_of_bins-1]. This function calculates the LUT.
def make_lut(min_value, max_value, number_of_bins):
    binsize = 1 + (max_value - min_value) / number_of_bins
    plut = []
    for i in range(min_value, max_value + 1):
        plut[i] = (i - min_value) / binsize
    return plut

