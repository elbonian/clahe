from clahelib import clahe
from PIL import Image

im = Image.open("images/snow_gray8_small.png")

import cProfile, pstats
cProfile.run("clahe(im, 63, 256, 3.0)", "{}.profile".format(__file__))
s = pstats.Stats("{}.profile".format(__file__))
s.strip_dirs()
s.sort_stats("time").print_stats(10)