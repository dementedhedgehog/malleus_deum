#!/usr/bin/env python2
# coding=utf-8
"""

    Walks the dir tree looking for licensing information
    for art and fonts.


"""
import os
from os.path import abspath, join, splitext, dirname, exists, basename
import json

fail_fast = False


def fail(msg):
    if fail_fast:
        raise Exception(msg)
    else:
        print msg
    return
        


class ImgInfo:
    info_lookup = {}

    def __init__(self):
        self.img_fnames = set()
        self.img_license = None # resource_license
        self.artist = None # artist
        self.source = None # source
        return

    @classmethod
    def parse(cls, img_fname, license_fname):        
        key = basename(license_fname)

        if key in cls.info_lookup:
            info = cls.info_lookup[key]
        else:
            info = ImgInfo()
            cls.info_lookup[key] = info
            
        info.img_fnames.add(img_fname)


        if not exists(license_fname):
            fail("License file missing %s" % license_fname)
            return
        
        f = file(license_fname)
        json_info = json.load(f)
        for attr, value in json_info.items():
            if attr == "license":
                info.img_license = value
            elif attr == "artist":
                info.artise = value
            elif attr == "source":
                info.source = value
            else:
                fail("Unknown license information %s in %s" %
                     (attr, license_fname))

        if info.img_license is None:
            fail("Missing license information 'license' in %s" %
                 license_fname)

        if info.artist is None:
            fail("Missing license information 'artist' in %s" %
                 license_fname)

        if info.source is None:
            fail("Missing license information 'source' in %s" %
                 license_fname)
        return

    def __str__(self):
        return "%s %s %s %s" % (
            ", ".join(self.img_fnames),
            self.img_license,
            self.artist,
            self.source)
    

def generate_license_report(project_dir):

    for dir_name, sub_dirs, files in os.walk(project_dir):
        #print dir_name
        for fname in files:
            
            base_fname, ext = splitext(fname)
            full_fname = join(dir_name, fname)

            # images..
            if ext in (".png", ".svg", ".jpg", "gif", "xcf"):
                license_fname = join(dir_name, base_fname + ".json")
                ImgInfo.parse(img_fname=full_fname,
                              license_fname=license_fname)
                
    return


if __name__ == "__main__":
    src_dir = dirname(__file__)
    project_dir = abspath(join(src_dir, ".."))
    generate_license_report(project_dir)

    print "----"
    for img_info in ImgInfo.info_lookup.values():
        print img_info
    
