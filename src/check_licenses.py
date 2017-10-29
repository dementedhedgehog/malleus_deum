#!/usr/bin/env python
# coding=utf-8
"""

    Walks the dir tree looking for licensing information
    for art and fonts.


"""
import os
from os.path import abspath, join, splitext, dirname, exists, basename
from PIL import Image, ExifTags




class Report:

    def __init__(self, fname, resource_license, artist, source):
        self.fname = fname
        self.license = resource_license
        self.artist = artist
        self.source = source
        return


def generate_license_report(project_dir):

    for dir_name, sub_dirs, files in os.walk(project_dir):
        print dir_name
        for fname in files:

            _, ext = splitext(fname)
            full_fname = join(dir_name, fname)
            
            if ext in (): # (".png", ".svg", ".jpg"):
                print('\t%s' % fname)

            elif ext in (".gif",
                         #".svg",
                         ".jpg"):
                #):
                print('\t%s' % fname)

                img = Image.open(full_fname)
                #exif = { ExifTags.TAGS[k]: v
                #         for k, v in img._getexif().items()
                #         if k in ExifTags.TAGS }
                #print exif

                info = img._getexif()
                print info


            elif ext == ".svg":
                print('\t%s' % fname)
                
                
            elif ext in (".ttf", ):
                print('\t%s' % fname)
                
        if '.git' in sub_dirs:
            sub_dirs.remove('.git')




if __name__ == "__main__":
    src_dir = dirname(__file__)
    project_dir = abspath(join(src_dir, ".."))
    generate_license_report(project_dir)
    
