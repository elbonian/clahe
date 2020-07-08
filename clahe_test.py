from clahe_par import clahe
from PIL import Image
import cProfile, pstats

pr = cProfile.Profile()
pr.enable()

im = Image.open("images/snow_gray8_small.tif")
new_image = clahe(im, 127, 64, 3.0)
new_image.save("images/output.png")

pr.disable()
ps = pstats.Stats(pr)
ps.strip_dirs()
ps.sort_stats("time").print_stats(10)