#!/usr/bin/env python2
# coding=utf-8
"""

    Walks the dir tree looking for licensing information for art and fonts.

    Find images by googling like this:
           site:deviantart.com creative commons golem
           https://pixabay.com/en/users/OpenClipart-Vectors-30363/?tab=popular

"""
import codecs
import collections
import json
import os
from os.path import abspath, join, splitext, dirname, exists, basename, relpath
import sys
import traceback
import xml.etree.cElementTree as et

from utils import (
    parse_xml,
    xml_tree_to_str,
    #validate_xml,
    get_error_context,
    #COMMENT,
    is_comment,
    resources_dir,
    build_dir,
    )


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

        # Urls where the resource came from.
        self.urls = []

        # Whatever additional information people feel like adding.
        self.notes = None
        return

    def get_label(self):
        """
        Return some semi-useful identification string

        """
        if self.info_fname:
            return self.info_fname
        elif self.fname:
            return self.fname
        else:
            return self.name

    def get_contents_desc(self):
        # NOTE: need to sanitize fields with underscores in them!
        return "[%s] %s %s" % (self.sig, sanitize(self.name), self.artist)

    def get_sig(self):
        return self.sig

    def get_fname(self):
        return self.fname

    def get_type(self):
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
        
        resource_doc = parse_xml(info_fname)
        if resource_doc is None:
            raise Exception("Can't parse license: %s" % info_fname)

        # errors = validate_xml(resource_doc)
        # # If there's been a validation error print some information about it
        # if errors is not None:

        #     err = Exception(f"Invalid xml {info_fname}!")
        #     for i, e in enumerate(errors):
        #         msg = str(e)
        #         context = get_error_context(info_fname, e.line)
        #         err.add_note(f"error: ({i}) {msg}\n{context}\n\n")
        #     raise err
        
        root = resource_doc.getroot()
        if root.tag != "licenseinfo":
            raise Exception("Bad xml looking for xml with a root tag "
                            f"of licenseinfo in {info_fname}")
        
        for child in list(root):
            if is_comment(child):
                pass

            tag = child.tag
            if child.text:
                text = str(child.text.strip())
            else:
                text = "Missing!"
        
            if tag == "sig":
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
                self.urls.append(text)
            elif tag == "notes":
                if self.notes is None:
                    self.notes = text
                else:
                    self.notes += "\n" + text
            else:
                fail("Unknown license information %s in %s" %
                     (tag, info_fname))
        return    
    
    def __str__(self):
        return (
            f"Name: {self.name}\n" + 
            f"Type: {self.resource_type}\n" +
            f"Artist: {self.artist}\n" +
            f"Artist Sig: {self.sig}\n" +
            f"Filename: {self.fname}\n" +
            f"License: {self.license}\n" +
            f"Info Filename: {self.info_fname}\n" +
            f"Source: {self.source}\n" +
            "".join(f"URL: {url}\n" for url in self.urls) +
            f"Used: {' '.join(self.used)}\n" +
            f"Status: {self.get_license_status()}\n")


class UsedResourcesDB:
    """
    A json database that lets us accumulate resource usage information
    across multiple build runs.  (Helps us clean up unused resources).

    """
    USED_RESOURCES_FNAME = join(build_dir, "used_resources.xml")

    def __init__(self):
        # dictionary that points from:  resource_id :--> set_of_filenames
        self.resources = collections.defaultdict(set)
        return

    def write(self):
        resources_elem = et.Element("usedresources")
        for resource_id, filenames in self.resources.items():        
            resource_elem = et.SubElement(resources_elem, "resource")
            resource_elem.set('id', resource_id)
            for filename in filenames:
                d = et.SubElement(resource_elem, "doc")
                d.set("fname", filename)

        # Write a human readable representation of the xml
        # (i.e. with spaces and newlines!)
        tree = et.ElementTree(resources_elem)
        et.indent(tree, space="    ")
        tree.write(self.USED_RESOURCES_FNAME)
        return                

    def read(self):
        if exists(self.USED_RESOURCES_FNAME):
            doc = parse_xml(self.USED_RESOURCES_FNAME)
            used_resources_elem = doc.getroot()

            for resource in list(used_resources_elem):
                if resource.tag == "resource":
                    resource_id = resource.attrib['id']
                    self.resources[resource_id] = set()
                    for d in resource:
                        fname = d.attrib.get("fname")
                        self.resources[resource_id].add(fname)
        return


    def is_used(self, resource_id):
        return resource_id in self.resources and len(self.resources) > 0
    
    def use(self, resource_id, filename):
        self.resources[resource_id].add(filename)

    def __str__(self):
        resource_ids = self.resources.keys()
        sorted(resource_ids)

        str_rep = "Used Resources:\n"
        for resource_id in resource_ids:
            filenames = self.resources[resource_id]
            filenames_str = " ".join(filenames)
            str_rep += f"{resource_id}: {filenames}\n"
        return str_rep
            
        

class Resources:
    """
    A database containing all the resources in the
    resources/ directory.

    """
    def __init__(self):
        self.resource_dirs = None
        self.lookup = {}
        self.used_resources_db = UsedResourcesDB()
        self.used_resources_db.read()
        return

    def use(self, resource_id, fname):
        resource = self.lookup[resource_id]
        self.used_resources_db.use(resource_id, fname)
        return resource

    def write_used_resources_db(self):
        self.used_resources_db.write()        
    
    def load(self, resource_dirs):
        for resource_dir in resource_dirs:

            # When loading resources fail slow.
            # (Print all the problems so we don't have to
            # reload over and over again).
            failed = False
            for dir_name, sub_dirs, files in os.walk(resource_dir):
                # look for a resource file.
                info_fnames = [fname for fname in files
                                        if fname.endswith(".xml")]
                for info_fname in info_fnames:

                    # 
                    info = ResourceInfo()
                    info_fname = join(dir_name, info_fname)
                    try:
                        info.parse(info_fname=info_fname)
                    except Exception as err:
                        #print(repr(err))
                        traceback.print_exc()
                        failed = True
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
            if failed:
                sys.exit()
        return        
    

    def print_report(self, verbose=False):
        """
        Check resources for art in the given list of resource dirs.

        """
        ok_resources = []
        # Note these two lists need not be mutually exclusive.
        no_license_resources = []
        unused_resources = []


        ids = list(self.lookup.keys())
        ids.sort()

        for resource_id in ids:

            used = self.used_resources_db.is_used(resource_id)
            info = self.lookup[resource_id]
            if used and info.license:
                ok_resources.append(info)

            if not info.license:
                no_license_resources.append(info)

            if not used:
                unused_resources.append(info)

        print("\n\n * Resource Report *")
        if verbose:
            print("\n**OK Resources**")
            for info in ok_resources:
                print(info.info_fname)
                
        if len(no_license_resources) > 0 or not verbose:
            print("\n** Missing License Resources **")
            for info in no_license_resources:
                print(info.info_fname)

        if len(unused_resources) > 0 or not verbose:
            print("\n** Unused Resources **")
            for info in unused_resources:
                print(info.info_fname)

            print("\n**Note**: the 'used' field is only accurate if "
              "you have built *all* the docs.\n\n")


if __name__ == "__main__":
    src_dir = dirname(__file__)
    root_dir = abspath(join(src_dir, ".."))    

    resource_dirs = (join(root_dir, "resources"),
                     join(root_dir, "unused_resources"))

    resources = Resources()
    resources.load(resource_dirs)
    #resources.print_report()
    for key in resources.lookup:
        print(key)

    
