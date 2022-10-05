import os


# local code.
import utils


modules_dir = utils.get_modules_dir()


def get_modules():
    for root, dirs, files in os.walk(modules_dir, topdown=False):
        for name in dirs:
            print(os.path.join(root, name))
