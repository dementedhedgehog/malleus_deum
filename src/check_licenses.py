#!/usr/bin/env python2
# coding=utf-8
"""

    Walks the dir tree looking for licensing information
    for art and fonts.


    Find images by googling like this:
           site:deviantart.com creative commons golem

"""
import os
from os.path import abspath, join, splitext, dirname, exists, basename#
from utils import parse_xml
import codecs
import sys

# Handle utf-8 characters on ascii consoles.
#UTF8Writer = codecs.getwriter('utf8')
#sys.stdout = UTF8Writer(sys.stdout)

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
        self.url = None
        self.notes = None
        return

    def get_artist(self):
        """Return artist as an ascii string."""
        if self.artist is not None:
            str_rep = self.artist.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    def get_license(self):
        """Return license as an ascii string."""
        if self.img_license is not None:
            str_rep = self.img_license.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    @classmethod
    def parse(cls, img_fname, license_fname):        
        key = basename(license_fname)

        if key not in cls.info_lookup:
            cls.info_lookup[key] = ImgInfo()

        info = cls.info_lookup[key]                        
        info.img_fnames.add(img_fname)

        if not exists(license_fname):
            #fail("License file missing %s" % license_fname)
            return
        
        doc = parse_xml(license_fname)
        root = doc.getroot()
        assert root.tag == "licenseinfo"


        for child in list(root):

           tag = child.tag
        
           #for attr, value in json_info.items():
           if tag == "license":
               info.img_license = unicode(child.text.strip())
           elif tag == "artist":
               info.artist = unicode(child.text.strip())
           elif tag == "artistfullname":
               info.artistfullname = unicode(child.text.strip())
           elif tag == "source":
               if child.text is not None:
                   info.source = unicode(child.text.strip())
           elif tag == "url":
               if child.text is not None:
                   info.url = unicode(child.text.strip())
           elif tag == "notes":
               info.notes = unicode(child.text.strip())
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

        if self.img_license:
            status = "OK"
        else:
            status = "*** MISSING LICENSE INFO ***"            
        
        return "%s %s %s %s %s" % (
            ", ".join(self.img_fnames),
            self.img_license,
            self.artist,
            self.source,
            status)
    

def generate_license_report(project_dir):

    for dir_name, sub_dirs, files in os.walk(project_dir):
        for fname in files:
            base_fname, ext = splitext(fname)
            full_fname = join(dir_name, fname)

            # images..
            if ext in (".png", ".svg", ".jpg", "gif", "xcf"):
                license_fname = join(dir_name, base_fname + ".xml")
                ImgInfo.parse(img_fname=full_fname,
                              license_fname=license_fname)
                
    return ImgInfo.info_lookup


if __name__ == "__main__":
    src_dir = dirname(__file__)
    root_dir = abspath(join(src_dir, ".."))
    img_license_info = generate_license_report(root_dir)

    n_chars = len(root_dir) + 1
    for img_info in img_license_info.values():
        if img_info.img_license:
            status = "OK"
        else:
            status = "*** MISSING LICENSE INFO ***"

        #if img_info.artist is not None:
        #    print img_info.artist.encode("ascii", "replace")
            
        print "%s %s %s %s %s" % (
            status,
            ", ".join([fname[n_chars:] for fname in img_info.img_fnames]),
            img_info.get_license(),
            img_info.get_artist(),
            img_info.source)
        
    
