#!/usr/bin/env python
"""


"""
from os.path import join, exists, dirname
from os import makedirs
from copy import deepcopy
import sys
import codecs
import traceback

from config import use_imperial
from utils import (
    normalize_ws,
    parse_xml,
    is_comment,
    node_to_string,
    get_error_context,
    get_alias,
)


# These attributes tell us to format their tokens differently.
TOKEN_TYPE = "token_type"
TOKEN_TYPE_KEYWORD = "keyword"
TOKEN_TYPE_ALIAS = "alias"
TOKEN_TYPE_ATOM = "atom"
TOKEN_TYPE_IGNORE_TEXT = "ignore-text"
TOKEN_TYPE_STRING_CONSTANT = "string-constant"


# These are image type tags.
IMG_TAGS = ("img", "handout")

# These tags don't need to go to the document formatter
# They contain metadata that's not meant for display..
# e.g. archetype metadata.
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
            raise Exception(
                "Can't find resources in a doc without a book node!")
        errors = []
        self._parse_resources(book_node, errors)
        return errors

    def _parse_resources(self, element, errors, in_comment=False):
        """
        FSM to find img resource ids.
        """
        #tag = element.tag
        #element_name = ("%s" % tag).lower()
        tag = ("%s" % element.tag).lower()

        if is_comment(element):
            in_comment = True
        elif tag in IMG_TAGS:
            if not in_comment and "id" in element.attrib:
                resource_id = element.get("id")
                self.resource_ids.append(resource_id)

        # handle all the children
        for child in list(element):
            self._parse_resources(child, errors, in_comment=in_comment)
        return

    def has_book_node(self):
        root = self.doc.getroot()
        book_nodes = root.xpath("//book")
        return len(book_nodes) == 1

    def get_book_node(self):
        """
        Returns the book in this doc (or None).
        We only format books.  Non-books are data.
        
        """
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

    def _create_error(self, msg, i_formatter, element) -> Exception:
        # This is the context within the xml where the error occured.
        stack_list = traceback.format_stack()
        stack_trace = ''.join(stack_list[:-1]) + "\n"
        if element.sourceline:
            sourceline = element.sourceline
            context = get_error_context(self.fname, element.sourceline)
        else:
            sourceline = "line??"
            context = "context??"
            
        return Exception(
            "====\n"
            f"{msg} element {i_formatter.__class__.__name__} "
            f"{stack_trace}"
            f"at {self.fname}:{sourceline}\n"
            f"{context}")
        
    def format(self, i_formatter):
        """
        Descend into the doc tree calling formatter callbacks to format
        the doc as we go.

        """
        book_node = self.get_book_node()
        if book_node is None:
            raise Exception("Can't format a doc without a book node!")
        errors = []

        # Build a lookup table of callback functions
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
        the formatter to deal with.
        """
        # Replace aliases early.
        if element.get(TOKEN_TYPE) == TOKEN_TYPE_ALIAS:
            element = get_alias(element)
        
        tag = ("%s" % element.tag).lower()
        
        if tag in NON_DOC_TAGS:
            # Don't bother parsing these metadata tags to the formater.
            return

        token_type = element.get(TOKEN_TYPE)                
        if token_type == TOKEN_TYPE_STRING_CONSTANT:
            i_formatter.handle_text(element.text)
        
        elif token_type == TOKEN_TYPE_KEYWORD:
            i_formatter.handle_keyword(element.text)
                            
        elif is_comment(element):
            i_formatter.start_comment(element)

        else:
            # handle tag by calling start_tag() and end_tag() bookend calls.
            handler_name = f"start_{tag}"
            if handler_name in methods:
                handler = methods[handler_name]       
                try:
                    handler(element)
                except Exception as err:
                    context = get_error_context(self.fname, element.sourceline)
                    err.add_note(context)
                    raise err
                    #raise self._get_error(err, i_formatter, element)
            else:
                raise self._create_error(
                    f"Unknown element <{tag}> or missing {handler_name}",
                    i_formatter,
                    element)
            
            # handle text.
            if element.text and token_type != TOKEN_TYPE_IGNORE_TEXT:
                text = element.text
                i_formatter.handle_text(text)
            
            # handle all the children
            if token_type != TOKEN_TYPE_ATOM:
                for child in list(element):
                    self._format(child, i_formatter, methods, errors)                

        if is_comment(element):
            i_formatter.end_comment(element)

        elif token_type == TOKEN_TYPE_KEYWORD:
            pass        

        elif token_type == TOKEN_TYPE_STRING_CONSTANT:            
            pass

        else:
            handler_name = f"end_{tag}"
            if handler_name in methods:
                handler = methods[handler_name]
                try:
                    handler(element)                    
                except Exception as err:
                    context = get_error_context(self.fname, element.sourceline)
                    err.add_note(context)
                    raise err
                
            else:
                raise self._create_error(
                    f"Missing xml element handler {handler_name}()",
                    i_formatter,
                    element)

        # handle trailing text.
        if element.tail:
            tail = element.tail
            i_formatter.handle_text(tail)            
        return
    
                
if __name__ == "__main__":
    from latex_formatter import LatexFormatter
    import utils
    from db import DB

    fname = "./test.xml"
    fout = "./test_out.xml"
    doc = Doc(fname)
    xml_doc = doc.parse()
    print(node_to_string(xml_doc.getroot()))
    
    db = DB()
    db.load(utils.root_dir)

    with codecs.open(fout, "w", "utf-8") as f:                   
        latex_formatter = LatexFormatter(f, db, fout)    
        doc.format(latex_formatter)
