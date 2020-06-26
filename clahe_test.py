from clahelib import clahe
from PIL import Image

im = Image.open("images/cell_gray16.tif")
clahe(im, 127, 256, 2.0)