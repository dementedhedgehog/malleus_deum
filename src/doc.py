#!/usr/bin/env python
"""


"""
# print without newline at the end.
from __future__ import print_function

from os.path import join, exists, dirname
from os import makedirs
from copy import deepcopy
import sys
import codecs
from utils import (
    normalize_ws,
    parse_xml, validate_xml,
    COMMENT,
    node_to_string,
    get_error_context
)


from latex_formatter import LatexFormatter


# These are tags we want to walk into.
# 
# This is a bit of a hack.. I should have organized the latex
# formatter better.. we use this to gradually get to how we want
# the formatters to all work, which is like html/xml with opening
# and closing tags and descending into tags recursively rather than
# hard coding element.text in the latex_writer.  Ultimately
# this would be all tags.. in the meanwhile that would cause chaos.
TEXT_TAGS = (
    "mbtitle", "mbtags",
    "mbac", "mbhp", "mbmove",
    "mbstr", "mbend", "mbag", "mbspd", "mbluck", "mbwil", "mbper",    
    "mbabilities", "mbaspects", "mbdescription", "mbinitiativebonus",
    "npcname", "npchps", "mbresolve", "mbmagic",
    "sectiontitle", "subsectiontitle", "subsubsectiontitle",
    "descriptions", "term", "description",
    "p",
    "td", "th", "version",
    "inspiration", "attribution",
    )


class Doc:

    def __init__(self, fname):
        # remember the filename for logging errors
        self.fname = fname
        self.doc = None
        # stack of ability groups 
        # self.ability_groups = []

        # list of resource ids.
        self.resource_ids = []
        return

    def parse(self):
        self.doc = parse_xml(self.fname)
        self._find_resource_ids()
        return self.doc

    def _find_resource_ids(self):
        book_node = self.get_book_node()
        if book_node is None:
            raise Exception("Can't find resources in a doc without a book node!")
        errors = []
        self._parse_resources(book_node, errors)
        return errors

    def _parse_resources(self, element, errors, in_comment=False):
        """
        FSM to find img resource ids.
        """
        tag = element.tag
        element_name = ("%s" % tag).lower()

        if tag is COMMENT:
            # i_formatter.start_comment(element)
            in_comment = True
        elif element_name == "img":
            if not in_comment and "id" in element.attrib:
                resource_id = element.get("id")
                self.resource_ids.append(resource_id)

        # handle all the children
        for child in list(element):
            self._parse_resources(child, errors, in_comment=in_comment)
        return

    
    def validate(self):
        valid = True        
        error = validate_xml(self.doc)

        # if there's been a validation error print some information about it
        if error is not None:
            print("Invalid xml %s!" % self.fname)
            print(error)

            # print out the context
            #print(get_error_context(self.fname, error.line))
            valid = False
        return valid

        
    def has_book_node(self):
        root = self.doc.getroot()
        book_nodes = root.xpath("//book")
        return len(book_nodes) == 1


    def get_book_node(self):
        """Returns the book in this doc (or None)."""
        # if it contains a book then format it!
        # otherwise carry on
        root = self.doc.getroot()
        book_nodes = root.xpath("//book")
        if len(book_nodes) == 0:
            return None
        assert len(book_nodes) <= 1
        book_node = book_nodes[0]
        return book_node


    def pretty_print(self):
        return node_to_string(self.doc.getroot(), pretty_print = True)


    def format(self, i_formatter):
        book_node = self.get_book_node()
        if book_node is None:
            raise Exception("Can't format a doc without a book node!")
        errors = []

        methods = {}
        for fn_name in dir(i_formatter):
            if fn_name.startswith("start_") or fn_name.startswith("end_"):
                fn = getattr(i_formatter, fn_name)
                if callable(fn):
                    methods[fn_name] = fn
                              
        self._format(book_node, i_formatter, methods, errors)
        return errors


    def _format(self, element, i_formatter, methods, errors):
        tag = element.tag
        element_name =  ("%s" % tag).lower()

        if tag is COMMENT:
            i_formatter.start_comment(element)
        else:            
            start_handler_name = "start_%s" % element_name
            if start_handler_name in methods:
                handler = methods[start_handler_name]

                try:
                    handler(element)
                except Exception as err:
                    context = get_error_context(self.fname, element.sourceline)
                    raise Exception("%s element %s formatter <%s> at %s:%s\n%s" % 
                              (str(err.message), i_formatter.__class__,
                               tag, self.fname, element.sourceline, context))
            else:
                errors.append("Unknown %s open element: <%s> at %s:%s\n%s" % 
                              (i_formatter.__class__, tag, self.fname, element.sourceline, 
                               get_error_context(self.fname, element.sourceline)))

        # handle trailing text.
        if element.tag in TEXT_TAGS and element.text:
            text = element.text # .strip()
            i_formatter.handle_text(text)
                
        # handle all the children
        for child in list(element):
            self._format(child, i_formatter, methods, errors)

        if tag is COMMENT:
            i_formatter.end_comment(element)
        else:
            end_handler_name = "end_%s" % element_name
            if end_handler_name in methods:
                handler = methods[end_handler_name]
                handler(element)                    
            else:
                errors.append("Unknown %s close element: </%s> at %s:%s\n%s" % 
                              (i_formatter.__class__, tag, self.fname, element.sourceline, 
                               get_error_context(self.fname, element.sourceline)))

        # handle trailing text.
        if element.tail:
            tail = element.tail
            i_formatter.handle_text(tail)
        return
    
                
if __name__ == "__main__":
    fname = "core.xml"
    doc = Doc(fname)
    doc.validate()

    with codecs.open("core.tex", "w", "utf-8") as f:               
        latex_formatter = LatexFormatter(f)
        doc.format(latex_formatter)
    # done.
