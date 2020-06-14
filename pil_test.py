import matplotlib.pyplot as plt
from PIL import Image

im = Image.open("images/cell_gray16.tif")
print("Format:\t\t" + im.format)
print("Size:\t\t" + str(im.size))
print("Mode:\t\t" + im.mode)

# Get pixel value at coord 0,0
pxdata = im.load()
print("Pixel at (0,0):\t" + str(pxdata[0,0]))

# Get image extrema
extrema = im.getextrema()
print("Extrema:\t" + str(extrema))

# Get histogram
histogram = im.histogram()
print("Histogram:")
print(histogram)

# Show visual histogram
# Could have used the 'histogram' variable and displayed a bar chart, though.
flattened_pxdata = im.getdata()
plt.hist(flattened_pxdata, 256)
plt.show()