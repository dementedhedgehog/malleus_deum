"""

  Utility methods including all the low level XML interface.


"""
import sys
from os.path import abspath, join, dirname
import codecs
import functools
import lxml
import io
from lxml.isoschematron import Schematron
import re
from functools import lru_cache
from copy import deepcopy
import io

# third party
from lxml import etree

# local
from config import use_imperial

class XMLException(Exception):
    """Raised when we have problems with xml."""
    pass


# directory constants
src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
ai_dir = join(root_dir, "ai")
build_dir = join(root_dir, "build")
pdfs_dir = join(root_dir, "pdfs")
docs_dir = join(root_dir, "docs")
fonts_dir = join(root_dir, "fonts")
resources_dir = join(root_dir, "resources")
char_sheet_dir = join(resources_dir, "character_sheets")
archetypes_dir = join(root_dir, "archetypes")
abilities_dir = join(root_dir, "abilities")
default_abilities_dir = join(abilities_dir, "defaults")
encounters_dir = join(root_dir, "encounters")
modules_dir = join(root_dir, "modules")
styles_dir = join(root_dir, "styles").replace("\\", "/")
release_dir = join(root_dir, "releases")
third_party_dir = join(src_dir, "third_party")
ability_groups_dir = join(root_dir, "abilities")


def is_filelike(obj):
    return isinstance(obj, io.IOBase)

@functools.cache
def _load_xsd_schema():
    schema_fname = abspath(join(dirname(__file__), "rpg.xsd"))
    schema = etree.parse(schema_fname)
    try:
        xml_schema = etree.XMLSchema(
            schema,
            # This tells etree to insert xsd 'fixed' and 'default' values
            # into the xml before parsing.  Required for keywordTypes.
            attribute_defaults=True,
        )
    except lxml.etree.XMLSchemaParseError as err:
        if hasattr(err, "message"):
            message = err.message
        else:
            message = str(err)
        raise lxml.etree.XMLSchemaParseError(
            "Problem parsing the schema doc: %s\n%s" % (schema_fname, message))
    return xml_schema


@functools.cache
def _load_schematron_validator():
    schematron_fname = abspath(join(dirname(__file__), "rpg.schematron"))
    schematron_doc = etree.parse(schematron_fname)
    schematron_validator = Schematron(schematron_doc, store_report=True)
    return schematron_validator


_ability_tokenizer = re.compile(
    "("
    # split on an ability or ability_id reference.
    "(?:"
    "✱✱?"                            # magic prefix characters
    r"(?:[a-zA-Z]+\.)?"              # optional ability group
    "(?:[a-zA-Z_]*[a-zA-Z])"         # ability name
    r"(?:\.[a-zA-Z]+)?"              # ability subability (for specializations)
    r"(?:\[[a-zA-Z_0-9\-\?/ ]+\])?"  # optional specialization
    "(?:_[0-9]+)?"                   # optional rank
    ")"
    # or a newline
    "|"
    "(?:\n)"
    ")"
)


def is_comment(element):
    return element.tag is etree.Comment
#COMMENT = etree.Comment


def split_ability_tokens(xml_str):
    """
    Extracts special ability tokens, e.g. ✱dagger.strike_1 from other text.

    """
    return _ability_tokenizer.split(xml_str)


def parse_xml_list(xml_node):
    """
    Parses xml like this: <xml_node> <A/> <B/><!-- a comment --><C/></xml_node>
    and returns a list like this: ["A", "B", "C"]

    Used for lists of keywords where we want the ids.
    """
    elements = []
    for child in list(xml_node):
        if not is_comment(child):
            elements.append(strip_xml(child.tag))
    return elements


def parse_xml_keyword_list(xml_node):
    """
    Parses xml like this:
    <xml_node> <a>A</a> <b>B</b><!-- a comment --><c>C</c></xml_node>
    and returns a list like this: ["A", "B", "C"]

    Used for lists of keywords where we want the text.
    """
    elements = []
    for child in list(xml_node):
        if not is_comment(child):
            elements.append(child.text.strip())
    return elements


def normalize_ws(text):
    """
    Latex is white space sensitive .. so strip any whitespace from the raw xml
    (as xml is whitespace agnostic) and replace with a single space.

    Leaves whitespace at front and back of string.

    """
    if text is None:
        return None

    if len(text) == 0:
        return ""

    leading_ws = " " if text[0].isspace() else ""
    trailing_ws = " " if text[-1].isspace() else ""
    return leading_ws + " ".join(text.split()) + trailing_ws        
        

def _perform_schematron_validation(xml_doc):
    """
    Runs the src/rpg.schematron rules over the xml docs.

    """
    # Jump through some hoops to make sure that when we get an error
    # the error context is accurate!.
    validator = _load_schematron_validator()
    validation_result = validator.validate(xml_doc)
    if not validation_result:

        # We've got a problem, now work out what it is.
        e = Exception(f"Schematron validation error!!!")        
        report = validator.validation_report
        for child in report.getiterator():
            tag = str(child.tag).replace(
                "{http://purl.oclc.org/dsdl/svrl}", "")

            match (child.__class__, tag):
                case (lxml.etree._Comment, _):
                    pass
                case (_, "schematron-output"):
                    pass
                case (_, "active-pattern"):
                    pass
                case (_, "fired-rule"):
                    pass
                case (_, "text"):
                    pass
                case (_, "failed-assert"):
                    test = child.get("test")
                    source_xpath = child.get("location")
                    element = xml_doc.xpath(source_xpath)[0]
                    sourceline = element.sourceline
                    tag = element.tag
                    message_element = child.getchildren()[0]
                    message = contents_to_string(message_element).strip()
                        
                    # Throw a schematron assert error with some context.
                    xml_str = node_to_string(xml_doc)
                    f = io.StringIO(xml_str)
                    context = get_error_context(f, sourceline, context_size=21)
                    e.add_note(
                        f"{context}\n"
                        f"*** {message} ***\n"
                        f"Assert [{test}]' failed at <{tag}> "
                        f"on line {sourceline}\n"
                        "N.B. the line number and error context are from "
                        "the modified xml\n"
                        "(after any includes have been processed).")
                    raise e                    
                    
                case _:
                    # Found something unexpected that may or may not be
                    # interesting.  That needs further investigation so
                    # we can decide to log or ignore it.
                    e.add_note(f"BUG? UNKNOWN CHILD {child.__class__} {tag}")
                    raise e
        raise e
    return


def parse_xml(fname, verbosity=0):
    try:
        try:        
            # Load the XSD
            etree.clear_error_log()
            xsd_schema = _load_xsd_schema()
            xsd_parser = etree.XMLParser(
                schema=xsd_schema,
                attribute_defaults=True,
                # Latex has problems with extra newlines in moving arguments
                # (e.g. index entries and section labels) so remove as much
                # of this as we can.
                remove_blank_text=True 
                #remove_blank_text=False
            )

            if verbosity > 1:
                print(f"\t\tXML Parsing: {fname}")
            
            # This does two things: i) it substitutes xsd "fixed" values into
            # the xml_str so that they're available for schematron to reason
            # about, and ii) it runs XSD validation on the xml.
            f = open(fname, "r")
            xml_doc = etree.parse(f)

            if verbosity>1:
                print(f"\t\tXML Validating Schema: {fname}")
            if not xsd_schema.validate(xml_doc):
                e = xsd_schema.error_log[0]
                context = get_error_context(
                    e.filename,
                    e.line,
                    context_size=21)
                
                raise XMLException(
                     f"XSD assert failed at {e.filename}:{e.line}\n"
                     f"{e}\n"
                     f"{context}\n"
                )
                            
        except lxml.etree.XMLSyntaxError as lxml_err:
            line, column = lxml_err.position
            msg = f" happens in file: {fname}:{line}:{column}"
            context = get_error_context(fname, line)
            lxml_err.add_note(msg + " " + context)
            xml_doc = None
            raise

        else:
            # Perform schematron validation on the modified tree.
            if verbosity>1:
                print(f"\t\tXML Validating Schematron: {fname}")
            
            _perform_schematron_validation(xml_doc)

    except Exception as err:
        err.add_note(f"Problem in file: {fname}")
        raise
    return xml_doc


def get_alias(element):
    """    
    
    """
    tag = element.text.lower()
    alias_element = etree.Element(tag)
    element.append(alias_element)
    return alias_element


def xml_tree_to_str(tree):
    """
    Pretty print xml tree for debugging.

    """
    xml_str = etree.tostring(tree, pretty_print=True)
    return xml_str.decode()


def node_to_string(node):
    """
    Returns all the nodes contents and its children as a string.

    """
    return etree.tostring(node, pretty_print=True, encoding="unicode")


def children_to_string(node):
    """
    Returns the nodes children as a string (just the xml elements), e.g.
    <node><a/><b/><c/></node> returns "<a/><b/><c/>".

    """
    return "".join([
        etree.tostring(c, pretty_print=True, encoding="unicode")
        for c in node.getchildren()
    ])


def contents_to_string(node):
    """
    Returns everything between the nodes tags <x>..</x> but NOT the tags
    themselves.

    FIXME: I think we want to migrate to contents_to_string2() and remove this.

    """
    return (node.text or "") + "".join(
        [etree.tostring(child, encoding="unicode")
         for child in node.iterchildren()])


def contents_to_string2(node):
    """
    Returns everything between the nodes tags <x>..</x> but NOT the tags
    themselves.

    e.g. contents_to_string2("<td> text1 <a> link </a> text2 </td>")
    returns "text1  link  text2"
    

    """
    return etree.tostring(node, method="text", encoding="unicode")


def contents_to_list(node):
    """
    Given <node><a/><b/><c/></node> returns a list ["a", "b", "c"]

    """
    return [child.tag for child in node.iterchildren()]


def contents_to_comma_separated_str(node):
    r"""
    Given <node><a/><b/><c/></node> returns a string a, b, c..

    """
    return (node.text or "") + ", ".join(contents_to_list(node))


def get_child_name(node):
    r"""
    Given <node><x/></node> returns "x".

    """
    children = list(node)
    return None if len(children) != 1 else strip_xml(children[0].tag)


def attrib_is_true(xml_node, attribute):
    """
    Returns True if the xml_node has the attribute specified and
    it's set to true.

    """
    value = False
    if attribute in xml_node.attrib:
        value_str = xml_node.get(attribute)
        if value_str == "true":
            value = True
        elif value_str != "false":
            raise Exception("Unexpected value for boolean in xml")
    return value


def get_error_context(file_or_filename, error_line_number, context_size=7):
    """
    Returns the neighbouring lines around an xml error for debug context.

    """
    context = ""
    try:
        # It's a filename?
        f = open(file_or_filename, "r")
    except TypeError:

        if is_filelike(file_or_filename):
            # It's a file!
            f = file_or_filename
        else:
            # No idea what this is!!
            raise Exception("Unknown object, "
                            "expecting a file or filename %s" %
                            file_or_filename)
    #finally:
    lines = f.readlines()
    from_line = max(error_line_number - context_size, 0)
    to_line = min(error_line_number + context_size, len(lines))
    for line_number in range(from_line, to_line):
        if line_number == error_line_number-1:
            ptr = "=>"
        else:
            ptr = "  "
            
        context += "%5s %2s %s" % (line_number, ptr, lines[line_number])
    return context


def convert_to_roman_numerals(number):
    """Converts a small int to Roman numerals (won't work on large ints)."""
    if number <= 0:
        number = 0
    elif number > 10:
        number = 10
    return ("0", "I", "II", "III", "IV", "V", "VI",
            "VII", "VIII", "IX", "X")[number]


def convert_str_to_bool(str_bool):
    return str_bool.lower() != "false"


def strip_xml(element_str):
    """Removes the < and /> around an element string."""
    if element_str.startswith("<") and element_str.endswith("/>"):
        return element_str[1:-2]
    return element_str


def convert_str_to_int(str_int):
    # later we might want some error handling!
    return int(str_int)


def convert_str_to_float(str_float):
    # later we might want some error handling!
    return float(str_float)


def parse_measurement_to_str(fname, measurement_node):
    # check at most once
    metric_found = False
    imperial_found = False

    # get the appropriate text representation.
    text_repr = ""
    for child in list(measurement_node):

        tag = child.tag
        if tag == "metric":
            if metric_found:
                raise NonUniqueTagError(tag, fname, child.sourceline)
            else:
                metric_found = True
                if not use_imperial:
                    text_repr += normalize_ws(child.text)

        elif tag == "imperial":
            if imperial_found:
                raise NonUniqueTagError(tag, self.fname, child.sourceline)
            else:
                imperial_found = True
                if use_imperial:
                    text_repr += normalize_ws(child.text)

        else:
            raise Exception(
                "UNKNOWN XML TAG (%s) File: %s Line: %s\n" %
                (tag, fname, child.sourceline))
    return text_repr


def get_child(node, child_name):
    r"""
    Given <node><x/><x/></node> then get_child_name 'x' returns the first x node.

    """
    return node.find(child_name)


def get_text_for_child(element, child_name):
    """
    Find text for a child element.

    """
    child = element.find(child_name)
    if child is None or child.text is None:
        text = ""
    else:
        text = child.text.strip()
    return text


_ability_regex = re.compile(
    "✱"
    "([a-zA-Z]+)"  # ability family
    r"\."
    r"([a-zA-Z_0-9\-\?]+)"  # ability name
    r"(?:\[([a-zA-Z_0-9\-\?]*)\])?"  # optional template?
    "(?:_([0-9]+))"  # optional level
)


def parse_ability_str(ability_str):
    """
    Takes something like this .. ✱lore.history[westreich]_2 and returns a tuple
    ("lore", "history", "westreich", 2).

    """
    match = _ability_regex.match(ability_str)
    return None if match is None else match.groups()


# def paginate(items, n_items_per_page):
#     """
#     Breaks a list of items up into a list of lists of a given size so we can fit
#     things on a page (e.g. for breaking a big list of abilities into multiple
#     tables).
    
#     """
#     pages = []
#     i = 0
#     page_num = 0
#     while i < len(items):
#         new_i = i + n_items_per_page
#         page = items[i:new_i]
#         pages.append(page)
#         i = new_i
#     return pages

def tabulate(items, n_lines_per_page, n_columns, n_lines_first_page=None):
    """
    Breaks a list of items up into a list of lists of a given size so we can fit
    things on a page (e.g. for breaking a big list of abilities into multiple
    tables).
    
    """
    pages = []
    
    i = 0
    finished = False
    while not finished:
        # Add a page
        page = []
        pages.append(page)

        if len(pages) == 1 and n_lines_first_page is not None:
            n_lines_this_page = n_lines_first_page
        else:
            n_lines_this_page = n_lines_per_page
        
        #
        for _ in range(n_lines_this_page):
            new_i = i + n_columns
            line = items[i:new_i]
            page.append(line)
            i = new_i

            if i >= len(items):
                finished = True
                break
        
    return pages




if __name__ == "__main__":    
    xml_doc = parse_xml("test.xml")
    print(node_to_string(xml_doc.getroot()))
    
