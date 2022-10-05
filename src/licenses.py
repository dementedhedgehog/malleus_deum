#!/usr/bin/env python2
# coding=utf-8
"""

    Walks the dir tree looking for licensing information
    for art and fonts.

    Find images by googling like this:
           site:deviantart.com creative commons golem
           https://pixabay.com/en/users/OpenClipart-Vectors-30363/?tab=popular

"""
import os
from os.path import abspath, join, splitext, dirname, exists, basename, relpath
from utils import parse_xml
import codecs
import sys
from utils import COMMENT

# Set this True to make missing license stuff a fatal error
fail_fast = True


def fail(msg):
    if fail_fast:
        raise Exception(msg)
    else:
        print(msg)
    return

def sanitize(text):
    return text.replace("_", "\_")

class ResourceInfo:

    def __init__(self):
        self.name = None
        self.resource_type = None
        self.sig = None # short identifier of the resource used in attribution.
        self.license_fname = None # name of the xml resource info file
        self.fname = None  # name of the resource file (potentially modified by us).
        self.resource_license = None # license CC by A etc.
        self.artist = None # artist
        self.source = None # source, general.. e.g. deviantart.com
        self.url = None # url where the resource came from.
        self.notes = None
        return

    def get_contents_desc(self):
        # NOTE: need to sanitize fields with underscores in them!
        return "[%s] %s %s" % (self.sig, sanitize(self.name), self.artist)

    def get_sig(self):
        if self.sig is None:
            raise Exception("Missing license information 'sig' in %s" %
                            self.license_fname)
        return self.sig

    def get_fname(self):
        if self.fname is None:
            raise Exception("Missing license information 'fname' in %s" %
                            self.license_fname)        
        return self.fname

    def get_type(self):
        if self.resource_type is None:
            raise Exception("Missing license information 'type' in %s" %
                            self.license_fname)        
        return self.resource_type

    def get_license_fname(self):
        return self.license_fname
    
    def get_artist(self):
        """Return artist as an ascii string."""
        if self.artist is not None:
            str_rep = self.artist.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    def get_license(self):
        """Return license as an ascii string."""
        if self.resource_license is not None:
            str_rep = self.resource_license.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    def parse(self, license_fname):
        self.license_fname = license_fname
        self.name = basename(license_fname)
        if not exists(license_fname):
            fail("License file missing %s" % license_fname)
            return
        
        doc = parse_xml(license_fname)
        if doc is None:
            raise Exception("Can't parse license: %s" % license_fname)
        root = doc.getroot()
        if root.tag != "licenseinfo":
            raise Exception("Bad xml looking for xml with a root tag of licenseinfo "
                            "in %s" % license_fname)
        
        for child in list(root):
           tag = child.tag
           if child.text is None:

               if tag not in ("source", "url", "notes"):
                   raise Exception("%s has empty value for %s" % (license_fname, tag))
               else:
                   text = u""
           else:
               #text = unicode(child.text.strip())
               text = str(child.text.strip())
        
           #for attr, value in json_info.items():
           if tag is COMMENT:
               pass
           elif tag == "sig":
               self.sig = text
           elif tag == "type":
               self.resource_type = text
           elif tag == "license":
               self.resource_license = text
           elif tag == "fname":
               # make all our filenames relative to this path (for portability)
               root_dir = abspath(join(dirname(__file__), ".."))
               relative_dir = relpath(dirname(license_fname), start=root_dir)
               self.fname = join(relative_dir, text)
           elif tag == "artist":
               self.artist = text
           elif tag == "artistfullname":
               self.artistfullname = text
           elif tag == "source":
                   self.source = text
           elif tag == "url":
                   self.url = text
           elif tag == "notes":
               self.notes = text
           else:
               fail("Unknown license information %s in %s" %
                    (tag, license_fname))

        if self.resource_license is None:
            fail("Missing license information 'license' in %s" %
                 license_fname)

        if self.artist is None:
            fail("Missing license information 'artist' in %s" %
                 license_fname)

        if self.source is None:
            fail("Missing license information 'source' in %s" %
                 license_fname)
        return

    
    def __str__(self):

        if self.resource_license:
            status = "OK"
        else:
            status = "*** MISSING LICENSE INFO ***"            
        
        return "%s %s %s %s %s" % (
            self.resource_fname,
            self.resource_license,
            self.artist,
            self.source,
            status)


class Licenses:

    def __init__(self):
        self.resource_dirs = None
        self.lookup = {}
        return

    def find(self, name):
        return self.lookup[name]
    
    def load(self, resource_dirs):
        print("-----------------")
        print(resource_dirs)
        for resource_dir in resource_dirs:
            for dir_name, sub_dirs, files in os.walk(resource_dir):

                print((dir_name, sub_dirs, files))
                #if dir_name == resource_dir:
                #    continue

                # look for a resource file.
                license_fnames = [fname for fname in files
                                        if fname.endswith(".xml")]
                #print(dir_name)
                #print(license_fnames)
                for license_fname in license_fnames:

                    # 
                    info = ResourceInfo()
                    license_fname = join(dir_name, license_fname)
                    info.parse(license_fname=license_fname)
                    key, _ = splitext(basename(license_fname))

                    print(license_fname)

                    # Check for duplicate resource license names.
                    if key in self.lookup:
                        existing_info = self.lookup[key]
                        raise Exception(
                            "License file names must be unique. "
                            "We have two or more license files called %s and %s"
                            % (license_fname,
                               existing_info.get_license_fname()))
                                        
                    self.lookup[key] = info

                #     # Now work out the resource file associated with th
                

                # if len(resource_files) > 1:
                #     raise Exception(
                #         "Only one resource file per resource dir. "
                #         "You can hide working files by prefixing the "
                #         "fileanme with an underscore '_'. "
                #         "More than one resource in %s, specifically:\n%s" %
                #         (dir_name, ", ".join(resource_files)))

                # elif len(resource_files) == 0:
                #     raise Exception("Resource dir contains no resources %s"
                #                     % dir_name)
                # else:
                #     fname = resource_files[0]
                #     # for fname in files:
                #     base_fname, ext = splitext(fname)
                #     full_fname = join(dir_name, fname)

                #     # images..
                #     #if ext in resource_extensions:
                #     #    if not fname.startswith("_"):
                #     license_fname = join(dir_name, base_fname + ".xml")

                #     key = basename(dir_name)
                #     if key not in self.lookup:
                        
                #     info = self.lookup[key]

                #     # if info.resource_fname is not None:
                #     info.resource_fname = fname
        return        
    
    # def load(self, resource_dirs):
    #     for resource_dir in resource_dirs:
    #         for dir_name, sub_dirs, files in os.walk(resource_dir):

    #             if dir_name == resource_dir:
    #                 continue

    #             resource_extensions = (".png", ".svg", ".jpg", "gif")
    #             resource_files = [fname for fname in files
    #                               if fname.endswith(resource_extensions)
    #                               and not fname.startswith("_")]

    #             if len(resource_files) > 1:
    #                 raise Exception(
    #                     "Only one resource file per resource dir. "
    #                     "You can hide working files by prefixing the "
    #                     "fileanme with an underscore '_'. "
    #                     "More than one resource in %s, specifically:\n%s" %
    #                     (dir_name, ", ".join(resource_files)))

    #             elif len(resource_files) == 0:
    #                 raise Exception("Resource dir contains no resources %s"
    #                                 % dir_name)
    #             else:
    #                 fname = resource_files[0]
    #                 # for fname in files:
    #                 base_fname, ext = splitext(fname)
    #                 full_fname = join(dir_name, fname)

    #                 # images..
    #                 #if ext in resource_extensions:
    #                 #    if not fname.startswith("_"):
    #                 license_fname = join(dir_name, base_fname + ".xml")

    #                 key = basename(dir_name)
    #                 if key not in self.lookup:
    #                     info = ResourceInfo()
    #                     info.parse(license_fname=license_fname)
    #                     self.lookup[key] = info
    #                 info = self.lookup[key]

    #                 # if info.resource_fname is not None:
    #                 info.resource_fname = fname
    #     return        

    def generate_license_report(self, root_dir):
        """
        Check licenses for art in the given list of resource dirs.

        """
        n_chars = len(root_dir) + 1
        for resource_info in self.lookup.values():

            if resource_info.resource_license:
                status = "OK"
            else:
                status = "*** MISSING LICENSE INFO ***"

            print("%s %s %s %s %s" % (
                status,
                resource_info.fname,
                resource_info.get_license(),
                resource_info.get_artist(),
                resource_info.source))
        return    


if __name__ == "__main__":
    src_dir = dirname(__file__)
    root_dir = abspath(join(src_dir, ".."))    

    resource_dirs = (join(root_dir, "resources"),
                     join(root_dir, "unused_resources"))

    license_info = generate_license_report(resource_dirs)

    n_chars = len(root_dir) + 1
    for img_info in license_info.values():
        if img_info.resource_license:
            status = "OK"
        else:
            status = "*** MISSING LICENSE INFO ***"

        print("%s %s %s %s %s" % (
            status,
            img_info.resource_fname,
            img_info.get_license(),
            img_info.get_artist(),
            img_info.source))
        
    
