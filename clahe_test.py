from clahelib import clahe_color
from PIL import Image
import cProfile, pstats
import ray

ray.init()

pr = cProfile.Profile()
pr.enable()

im = Image.open("images/timpanogos_small.tif")
code, new_image = clahe_color(im, 63, 256, 2.5, 5)
if code == 0:
    new_image.save("images/output.png")

pr.disable()
ps = pstats.Stats(pr)
ps.strip_dirs()
ps.sort_stats("time").print_stats(10)