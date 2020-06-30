from clahelib import clahe
from PIL import Image

im = Image.open("images/snow_gray8_small.tif")
clahe(im, 127, 64, 3.0)