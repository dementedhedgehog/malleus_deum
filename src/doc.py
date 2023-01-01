#!/usr/bin/env python
"""


"""
# print without newline at the end.
from __future__ import print_function # FIXME: should be able to get rid of this?

from os.path import join, exists, dirname
from os import makedirs
from copy import deepcopy
import sys
import codecs

from config import use_imperial
from utils import (
    normalize_ws,
    parse_xml, validate_xml,
    COMMENT,
    node_to_string,
    get_error_context
)


# These are tags we want to walk into.
# 
# This is a bit of a hack.. I should have organized the latex
# formatter better.. we use this to gradually get to how we want
# the formatters to all work, which is like html/xml with opening
# and closing tags and descending into tags recursively rather than
# hard coding element.text in the latex_writer.  Ultimately
# this would be all tags.. in the meanwhile that would cause chaos.
#
# In the long run this should be all tags.
TEXT_TAGS = (
    "corollary", "corollarytitle", "corollarybody",
    "mbtitle", "mbtags",
    "mbac", "mbhp", "mbmove",
    "mbstr", "mbend", "mbag", "mbspd", "mbluck", "mbwil", "mbper",    
    "mbabilities", "mbaspects", "mbdescription", "mbinitiativebonus",
    "npcname", "npchps", "mbresolve", "mbmagic",
    "sectiontitle", "subsectiontitle", "subsubsectiontitle", "abilitytitle",
    "leveltitle", "branchtitle", "pathtitle", 
    "descriptions", "term", "description", 
    "p", 
    "principle", "principletitle", "principlebody",
    "td", "th", "version",
    "inspiration", "attribution",
    "label", "smaller",
    "hline",
    )

# These are image type tags.
IMG_TAGS = ("img", "handout")

# These tags don't need to go to the document formatter
# (They contain metadata.. e.g. archetype metadata).
NON_DOC_TAGS = (
    "streams",
    "stream",
    "levelstamina",
    "levelhealth",
    "levelhealthrefresh",
    "levelluck",
    "levelluckrefresh",
    "levelmagic",
    "levelmagicrefresh",
    "levelmettle",
    "levelmettlerefresh",
)


class Doc:
    """
    Represents an xml doc.  We build pdfs etc from these.

    """
    def __init__(self, fname):
        # remember the filename for logging errors
        self.fname = fname

        # the doc xml dom
        self.doc = None

        # list of resource ids.
        self.resource_ids = []
        return

    def parse(self):
        self.doc = parse_xml(self.fname)
        if self.doc is not None:
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
        elif element_name in IMG_TAGS:
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
            valid = False
        return valid


    def has_book_node(self):
        root = self.doc.getroot()
        book_nodes = root.xpath("//book")
        return len(book_nodes) == 1


    def get_book_node(self):
        """Returns the book in this doc (or None)."""
        # if the xml contains a book then we'll want to format it!
        # otherwise carry on
        if self.doc is None:
            return None
        
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
        """
        Recursively descend into the doc structure.. handing nodes off to 
        the formatter to  deal with.
        """
        tag = element.tag
        element_name =  ("%s" % tag).lower()

        # Don't bother passing these metadata tags to the formater.
        if tag in NON_DOC_TAGS:
            return        
        
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
                              (str(err), i_formatter.__class__,
                               tag, self.fname, element.sourceline, context))
            else:
                errors.append("Unknown %s open element: <%s> at %s:%s\n%s" % 
                              (i_formatter.__class__, tag, self.fname, element.sourceline, 
                               get_error_context(self.fname, element.sourceline)))

        # handle trailing text.
        if element.tag in TEXT_TAGS and element.text:
            text = element.text
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

    from latex_formatter import LatexFormatter
    with codecs.open("core.tex", "w", "utf-8") as f:               
        latex_formatter = LatexFormatter(f)
        doc.format(latex_formatter)
    # done.
