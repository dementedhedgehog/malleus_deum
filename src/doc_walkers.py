"""

   Vistor Pattern for the XML doc tree.

   Document formatters are visitors, and we also run a preprocessor (another
   visitor) over the doc tree to add meta data (though it doesn't do a whole lot
   yet, ideally we'd add more meta-data which would let the formatters be
   simpler).

"""
import re
from abc import ABC, abstractmethod

import config
import utils


handle_regex = re.compile(r"^handle_")


def no_op(doc_processor, xml_element):
    """
    We've got a lot of xml tag handlers that don't need to do anything...
    Do nothing once, and do it here.
    """
    pass


class AbstractDocProcessor(ABC):
    """
    Interface shared by things that walk the xml doc tree, currently that is the
    Preprocessor and the Document Formatters.

    The Doc object is in charge of running preprocessors nad formatters over
    the document tree.

    """    
    @abstractmethod
    def get_start_method(self, tag: str):
        """All subclasses must implement this method."""
        pass

    @abstractmethod
    def get_end_method(self, tag: str):
        """Concrete method: Subclasses inherit this automatically."""
        pass

    @abstractmethod
    def process_plain_text(self, text):
        """
        Handles blocks of plain text with no embedded elements in it.
        
        """
        pass
    
    def _no_op(self, element):
        """
        We want a bound no_op method (this one) *and* an unbound no_op method.
        
        We always want to call the underlying no_op() with the same arguments,
        i.e. with no_op(doc_processor, xml_element) args... sometimes it helps
        with debugging.  Having things all loosey-goosey can get confusing.

        We want the bound _no_op() for setting handler methods in this file.

        We want the unbound no_op() for setting methods directly in the doc
        formatter implementation, e.g. in LatexFormatter we can have:
           start_section = no_op

        (We could just use start_section = self._no_op but we're trading a
        little extra complexity here for a little more brevity in the doc
        formatters themselves).
        
        """
        no_op(self, element)

        
class BaseDocFormatter(AbstractDocProcessor):
    """
    Logic common to all doc formatters.

    """
    def __init__(self):
        # A lookup table from handler name to handler fn e.g.
        # maps the string "start_section" ==> this_formatter.start_section() fn.
        self.methods = None
        return
    
    def _build_methods(self):        
        """
        Builds the methods lookup table of element handlers fns we extract from
        the formatter, e.g. things like start_section() and end_section()

        """
        # Build a lookup table of callback functions
        self.methods = {}
        for fn_name in dir(self):
            if fn_name.startswith("start_") or fn_name.startswith("end_"):
                fn = getattr(self, fn_name)
                if callable(fn):
                    self.methods[fn_name] = fn

            elif fn_name.startswith("handle_"):
                # methods with handle_foo() get converted into start and end
                # handlers as follows: start_foo->handle_foo, end_foo->no_op.
                start_fn_name = handle_regex.sub("start_", fn_name)
                end_fn_name = handle_regex.sub("end_", fn_name)
                fn = getattr(self, fn_name)
                if callable(fn):
                    self.methods[start_fn_name] = fn
                    self.methods[end_fn_name] = self._no_op

        # Now handle all the pass through elements
        # Pass through elements are ALL handled by pass_through_handler()
        assert callable(self.pass_through_handler)
        for tag in self.get_pass_through_elements():
            start_fn_name = f"start_{tag}"
            assert start_fn_name not in self.methods
            self.methods[start_fn_name] = self.pass_through_handler
            
            end_fn_name = f"end_{tag}"
            assert end_fn_name not in self.methods
            self.methods[end_fn_name] = self._no_op
        return

    @abstractmethod
    def get_pass_through_elements():
        """
        Return a list of element tags that are translated natively by the
        formatter with minimal or no work by the formatter.  We cause these
        Pass-Through elements

        """
        pass

    @abstractmethod
    def pass_through_handler(element):
        """
        This is the handler used to handle the pass through elements. Implement
        this to format simple stuff.

        """
        pass

    #
    # Get the start and end handlers
    # 
    def get_start_method(self, tag: str):
        """All subclasses must implement this method."""        
        handler_name = f"start_{tag}"
        if not self.methods:
            self._build_methods()
        return self.methods[handler_name]

        
    def get_end_method(self, tag: str):
        """Concrete method: Subclasses inherit this automatically."""
        handler_name = f"end_{tag}"
        return self.methods[handler_name]

    #
    # Handlers that should be common to all doc types?  Mainly for aliases?
    #
    def handle_measurement(self, distance):
        """
        Shared handling of measurements

        """
        if config.use_imperial:
            distance_text = utils.get_text_for_child(distance, "imperial")
            if distance_text is None:
                raise Exception("Imperial distance not specified!")

        else:
            distance_text = utils.get_text_for_child(distance, "metric")
            if distance_text is None:
                raise Exception("Metric distance not specified!")

        self.buffer.write(utils.normalize_ws(distance_text).strip())
        # FIXME REF TO BUFFER HERE IS BROKEN! process_text?
        return
    




class DocTreePreprocessor(AbstractDocProcessor):
    """
    When formatting we don't take the doc xml and build an abstract syntax
    tree (like compilers do). We just hand each element over to the
    formatter to format without any additional context.  This lack of
    context can be a problem for latex so we run a preprocessor across the
    doc tree and annotate it with any useful context we require.

    To solve that problem we run the book through a preprocessor that
    can annotate the xml nodes with additional data useful to the latex
    formatter.        

    """            
    PP_IS_FIRST_TABLE_ROW = "is_first_table_row"
    PP_IS_LAST_TABLE_ROW = "is_last_table_row"

    def __getattr__(self, name):
        """
        Do nothing unless we specifically say otherwise

        """
        return self._no_op
    
    def get_start_method(self, tag: str):
        """All subclasses must implement this method."""
        handler_name = f"start_{tag}"
        return getattr(self, handler_name) 
       
    def get_end_method(self, tag: str):
        """Concrete method: Subclasses inherit this automatically."""
        handler_name = f"end_{tag}"
        return getattr(self, handler_name)

    def start_table(self, table):
        # find how many rows and mark the first and last table row
        # (latex is stupid about formatting table rows).
        first_table_row = None
        last_row = None
        for child in table:
            if child.tag in ("tablerow", "tableheaderrow"):
                if first_table_row is None:
                    first_table_row = child
                last_table_row = child

        first_table_row.set(self.PP_IS_FIRST_TABLE_ROW, "true")
        last_table_row.set(self.PP_IS_LAST_TABLE_ROW, "true")
        return
    
    def process_plain_text(self, text):
        """
        Handles blocks of plain text with no embedded elements in it.
        
        """
        pass

    #
    # Helpers
    #
    @classmethod
    def is_first_table_row(cls, element):
        return utils.attrib_is_true(element, cls.PP_IS_FIRST_TABLE_ROW)

    @classmethod
    def is_last_table_row(cls, element):
        return utils.attrib_is_true(element, cls.PP_IS_LAST_TABLE_ROW)
