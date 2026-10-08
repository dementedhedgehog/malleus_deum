#!/usr/bin/env python
"""


"""
from os.path import join, exists, dirname
from os import makedirs
from copy import deepcopy
import sys
import codecs
import traceback
import re

from config import use_imperial
from utils import (
    normalize_ws,
    parse_xml,
    is_comment,
    node_to_string,
    get_error_context,
    get_alias,
)
from doc_walkers import DocTreePreprocessor



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

        # has the preprocessor been run?
        self.preprocessed = False

        # list of used resource ids (to keep track of what images we've used).
        self.resource_ids = []
        return

    def parse(self):
        self.doc = parse_xml(self.fname)
        if self.doc is not None:
            self._find_resource_ids()
        return self.doc

    
    def _find_resource_ids(self):
        """
        Keep track of the ids for the images we use.

        """
        book_node = self.get_book_node()
        if book_node is None:
            raise Exception(
                "Can't find resources in a doc without a book node!")
        errors = []
        self._parse_resources(book_node, errors)
        return errors

    def _parse_resources(self, element, errors, in_comment=False):
        """
        FSM to find img resource ids using recursive descent.
        
        """
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
        """
        Return True if the xml doc has a single <book> node.

        """
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
        # FIXME: isn't there duplicate logic for this in xml_utils or somewhere?
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


    def _preprocess(self, book_node, errors = []):
        if not self.preprocessed:
            preprocessor = DocTreePreprocessor()            
            self._format(book_node, preprocessor, errors)
            self.preprocesed = True
        return errors
        
            
    def format(self, i_formatter):
        """
        Descend into the doc tree calling formatter callbacks to format
        the doc as we go.

        There are two sorts of formatter callbacks we deal with e.g
        (start_section, end_section) pairs and handle_divider (we treat the
        handle methods as if they were a (handle_divider, no_op) pair

        """
        book_node = self.get_book_node()
        if book_node is None:
            raise Exception("Can't format a doc without a book node!")

        errors = []
        self._preprocess(book_node, errors)
        self._format(book_node, i_formatter, errors)
        return errors

    def _format(self, element, i_formatter, errors):
        """
        Recursively descend into the doc structure.. handing nodes off to 
        the formatter to deal with.
        """
        # Replace aliases early.
        if element.get(TOKEN_TYPE) == TOKEN_TYPE_ALIAS:
            element = get_alias(element)
        
        tag = ("%s" % element.tag).lower()
        
        # Don't bother passing these metadata tags to the formater.
        if tag in NON_DOC_TAGS:
            return

        token_type = element.get(TOKEN_TYPE)
        if token_type == TOKEN_TYPE_STRING_CONSTANT:
            i_formatter.process_plain_text(element.text)
        
        elif token_type == TOKEN_TYPE_KEYWORD:
            i_formatter.handle_keyword(element.text)
                            
        elif is_comment(element):
            i_formatter.start_comment(element)

        else:
            # call start_tag() 
            handler = i_formatter.get_start_method(tag)
            if handler:
                try:
                    handler(element)                    
                except Exception as err:
                    context = get_error_context(self.fname, element.sourceline)
                    err.add_note(f"Handling start_{tag}()")
                    err.add_note(context)
                    raise err
            else:
                raise self._create_error(
                    f"Unknown element <{tag}> or missing {handler_name}",
                    i_formatter,
                    element)
            
            # handle text.
            if element.text and token_type != TOKEN_TYPE_IGNORE_TEXT:
                text = element.text
                i_formatter.process_plain_text(text)
            
            # handle all the children
            if token_type != TOKEN_TYPE_ATOM:
                for child in list(element):
                    self._format(child, i_formatter, errors)                

        if is_comment(element):
            i_formatter.end_comment(element)

        elif token_type == TOKEN_TYPE_KEYWORD:
            pass        

        elif token_type == TOKEN_TYPE_STRING_CONSTANT:            
            pass

        else:
            # call end_tag().
            handler = i_formatter.get_end_method(tag)
            if handler:
                try:
                    handler(element)
                except Exception as err:
                    context = get_error_context(self.fname, element.sourceline)
                    err.add_note(f"Handling end_{tag}()")
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
            i_formatter.process_plain_text(tail)
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
