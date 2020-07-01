from clahe_par import clahe
from PIL import Image
import cProfile, pstats

im = Image.open("images/snow_gray8_small.tif")
cProfile.run("clahe(im, 127, 64, 3.0)","{}.profile".format(__file__))
s = pstats.Stats("{}.profile".format(__file__))
s.strip_dirs()
s.sort_stats("time").print_stats(10)
