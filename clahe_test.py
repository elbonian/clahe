from clahelib import clahe
from PIL import Image

im = Image.open("images/insight_gray8.tif")
clahe(im, 63, 256, 3.0)