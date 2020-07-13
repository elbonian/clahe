from clahe_par import clahe_bw
from PIL import Image
import cProfile, pstats

pr = cProfile.Profile()
pr.enable()

im = Image.open("images/snow_gray8_small.tif")
code, new_image = clahe_bw(im, 127, 128, 3.0)
if code == 0:
    new_image.save("images/output.png")

pr.disable()
ps = pstats.Stats(pr)
ps.strip_dirs()
ps.sort_stats("time").print_stats(10)