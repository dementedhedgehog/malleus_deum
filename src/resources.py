#!/usr/bin/env python2
# coding=utf-8
"""

    Walks the dir tree looking for licensing information for art and fonts.

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
    return text.replace("_", r"\_")


class ResourceInfo:
    """
    Information about some art.. author, license, source etc.

    """
    def __init__(self):
        # 
        self.name = None

        # Type of resource.. art or font?
        self.resource_type = None

        # short id of the artist used in attribution.
        self.sig = None
        
        # filename of the resource file e.g. /foo/bar.png
        self.fname = None

        # license, e.g. CC by
        # This is an xml record that we write that lives in the
        # same dir as the resource and that contains all the
        # relevant information we need.
        self.license = None

        # name of the xml resource info file
        self.info_fname = None
        
        # artist name
        self.artist = None

        # source, the website we found the resource e.g. deviantart.com
        self.source = None 

        # Url where the resource came from.
        self.url = None

        # Whatever additional information people feel like adding.
        self.notes = None

        # Is this resource used anywhere?
        # In order to gather this info we need to build docs.  So
        # something has to tell us when they use the resource.
        self.used = False
        return

    def get_contents_desc(self):
        # NOTE: need to sanitize fields with underscores in them!
        return "[%s] %s %s" % (self.sig, sanitize(self.name), self.artist)

    def get_sig(self):
        if self.sig is None:
            raise Exception("Missing license information 'sig' in %s" %
                            self.info_fname)
        return self.sig

    def get_fname(self):
        if self.fname is None:
            raise Exception("Missing license information 'fname' in %s" %
                            self.info_fname)        
        return self.fname

    def get_type(self):
        if self.resource_type is None:
            raise Exception("Missing license information 'type' in %s" %
                            self.info_fname)        
        return self.resource_type

    def get_info_fname(self):
        return self.info_fname
    
    def get_artist(self):
        """Return artist as an ascii string."""
        if self.artist is not None:
            str_rep = self.artist.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    def get_license(self):
        """Return license as an ascii string."""
        if self.license is not None:
            str_rep = self.license.encode("ascii", "replace")
        else:
            str_rep = "None"
        return str_rep

    def get_license_status(self):
        if self.license:
            license_status = "OK"
        else:
            license_status = "*** MISSING LICENSE INFO ***"
        return license_status

    def parse(self, info_fname):
        self.info_fname = info_fname
        self.name = basename(info_fname)
        if not exists(info_fname):
            fail("License file missing %s" % info_fname)
            return
        
        doc = parse_xml(info_fname)
        if doc is None:
            raise Exception("Can't parse license: %s" % info_fname)
        root = doc.getroot()
        if root.tag != "licenseinfo":
            raise Exception("Bad xml looking for xml with a root tag "
                            f"of licenseinfo in {info_fname}")
        
        for child in list(root):
           tag = child.tag
           if child.text is None:
               if tag not in ("source", "url", "notes"):
                   raise Exception("%s has empty value for %s" %
                                   (info_fname, tag))
               else:
                   text = u""
           else:
               #text = unicode(child.text.strip())
               text = str(child.text.strip())
        
           if tag is COMMENT:
               pass
           elif tag == "sig":
               self.sig = text
           elif tag == "type":
               self.resource_type = text
           elif tag == "license":
               self.license = text
           elif tag == "fname":
               # make all our filenames relative to this path (for portability)
               root_dir = abspath(join(dirname(__file__), ".."))
               relative_dir = relpath(dirname(info_fname), start=root_dir)
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
                    (tag, info_fname))

        if self.license is None:
            fail("Missing license information 'license' in %s" %
                 info_fname)

        if self.artist is None:
            fail("Missing license information 'artist' in %s" %
                 info_fname)

        if self.source is None:
            fail("Missing license information 'source' in %s" %
                 info_fname)
        return

    
    def __str__(self):        
        return (
            f"Name: {self.name}\n"
            f"Type: {self.resource_type}\n"
            f"Artist: {self.artist}\n"
            f"Artist Sig: {self.sig}\n"
            f"Filename: {self.fname}\n"
            f"License: {self.license}\n"
            f"Info Filename: {self.info_fname}\n"
            f"Source: {self.source}\n"
            f"URL: {self.url}\n"
            f"Used: {self.used}\n"
            f"Status: {self.get_license_status()}\n")


class Resources:

    def __init__(self):
        self.resource_dirs = None
        self.lookup = {}
        return

    def use(self, name):
        resource = self.lookup[name]
        resource.used = True
        return resource
    
    def load(self, resource_dirs):
        for resource_dir in resource_dirs:
            for dir_name, sub_dirs, files in os.walk(resource_dir):

                # look for a resource file.
                info_fnames = [fname for fname in files
                                        if fname.endswith(".xml")]
                for info_fname in info_fnames:

                    # 
                    info = ResourceInfo()
                    info_fname = join(dir_name, info_fname)
                    info.parse(info_fname=info_fname)
                    key, _ = splitext(basename(info_fname))

                    # Check for duplicate resource names.
                    if key in self.lookup:
                        existing_info = self.lookup[key]
                        raise Exception(
                            "Resource file names must be unique. "
                            "We have two or more resource files called %s and %s"
                            % (info_fname,
                               existing_info.get_info_fname()))
                                        
                    self.lookup[key] = info
        return        
    

    def print_report(self, verbose=False):
        """
        Check resources for art in the given list of resource dirs.

        """
        ok_resources = []
        # Note these two lists need not be mutually exclusive.
        no_license_resources = []
        unused_resources = []

        sorted_resource_infos = sorted(
            self.lookup.values(),
            key=lambda info: info.name)
        
        for info in sorted_resource_infos:
            if info.used and info.license:
                ok_resources.append(info)

            if not info.license:
                no_license_resources.append(info)

            if not info.used:
                unused_resources.append(info)

        print("\n\n * Resource Report *")
        if verbose:
            print("\n**OK Resources**")
            for info in ok_resources:
                print(info.name)
                
        if len(no_license_resources) > 0 or not verbose:
            print("\n** Missing License Resources **")
            for info in no_license_resources:
                print(info.name)

        if len(unused_resources) > 0 or not verbose:
            print("\n** Unused Resources **")
            for info in unused_resources:
                print(info.name)

        print("\n**Note**: the 'used' field is only accurate if "
              "you have built *all* the docs.\n\n")


if __name__ == "__main__":
    src_dir = dirname(__file__)
    root_dir = abspath(join(src_dir, ".."))    

    resource_dirs = (join(root_dir, "resources"),
                     join(root_dir, "unused_resources"))

    resources = Resources()
    resources.load(resource_dirs)
    resources.print_report()
