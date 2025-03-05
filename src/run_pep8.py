
import os
from os.path import join, abspath, dirname, splitext

try:
    import pycodestyle
except ImportError:
    import pep8 as pycodestyle


src_dir = abspath(join(dirname(__file__)))
fnames = []
for root, dirs, files in os.walk(src_dir, topdown=False):
    for name in files:
        fname = join(root, name)

        _, ext = splitext(fname)
        if ext == ".py":
            if "third_party" in fname:
                continue
            fnames.append(fname) 

style = pycodestyle.StyleGuide()
result = style.check_files(fnames)
