from clahe_prototype import clahe
from PIL import Image

im = Image.open("images/cell_gray16.tif")
clahe(im, 2, 2, 128, 2.0)