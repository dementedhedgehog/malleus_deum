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
from utils import normalize_ws


from latex_formatter import LatexFormatter
from parser_utils import parse_xml, validate_xml, COMMENT, node_to_string, get_error_context


class Doc:

    def __init__(self, fname):
        # remember the filename for logging errors
        self.fname = fname
        self.doc = None
        # stack of ability groups 
        self.ability_groups = []
        return

    def parse(self):
        self.doc = parse_xml(self.fname)
        return self.doc

        
    def validate(self):
        valid = True        
        error = validate_xml(self.doc)

        # if there's been a validation error print some information about it
        if error is not None:
            print("Invalid xml %s!" % self.fname)
            print(error)

            # print out the context
            print(get_error_context(self.fname, error.line))
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
                handler(element)                
            else:
                errors.append("Unknown open element: <%s> at %s:%s\n%s" % 
                              (tag, self.fname, element.sourceline, 
                               get_error_context(self.fname, element.sourceline)))            
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
                errors.append("Unknown close element: </%s> at %s:%s\n%s" % 
                              (tag, self.fname, element.sourceline, 
                               get_error_context(self.fname, element.sourceline)))        
        # handle all the children
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
