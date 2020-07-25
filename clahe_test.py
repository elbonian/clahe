from clahelib_par import clahe_bw
from PIL import Image
import cProfile, pstats

pr = cProfile.Profile()
pr.enable()

im = Image.open("images/insight_gray8.tif")
code, new_image = clahe_bw(im, 63, 256, 3.0, 0)
if code == 0:
    new_image.save("images/output.png")

pr.disable()
ps = pstats.Stats(pr)
ps.strip_dirs()
ps.sort_stats("time").print_stats(10)