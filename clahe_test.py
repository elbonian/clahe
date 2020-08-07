from clahelib import clahe_color
from clahelib import clahe_bw
from PIL import Image
import cProfile, pstats
import ray

# Initialize ray
ray.init()

# These 2 lines are only needed if algorithm needs to be profiled.
pr = cProfile.Profile()
pr.enable()

""" Invocation example
This might take anywhere from seconds to minutes
depending on computer type, image, and parameters passed.
"""
im = Image.open("images/timpanogos_small.tif")
#new_image = clahe_color(im, 63, 256, 2.5)
new_image = clahe_color(im, 0, 0, 0)
new_image.save("images/output.png")

# These 4 lines are only needed if algorithm needs to be profiled.
pr.disable()
ps = pstats.Stats(pr)
ps.strip_dirs()
ps.sort_stats("time").print_stats(10)