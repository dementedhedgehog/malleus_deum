"""

  Utility methods.
  Hide lxml calls here.


"""
import sys
from os.path import abspath, join, dirname
import codecs
import lxml
from lxml.isoschematron import Schematron
import re
from functools import lru_cache
from copy import deepcopy

# third party
from lxml import etree

# local
from config import use_imperial

COMMENT = etree.Comment

# directory constants
root_dir = abspath(join(dirname(__file__), ".."))
src_dir = abspath(join(dirname(__file__)))
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


def load_xsd_schema():
    schema_fname = abspath(join(dirname(__file__), "rpg.xsd"))
    schema = etree.parse(schema_fname)
    try:
        xml_schema = etree.XMLSchema(schema)
    except lxml.etree.XMLSchemaParseError as err:
        if hasattr(err, "message"):
            message = err.message
        else:
            message = str(err)
        raise lxml.etree.XMLSchemaParseError(
            "Problem parsing the schema doc: %s\n%s" % (schema_fname, message))
    return xml_schema


def load_schematron_validator():
    schematron_fname = abspath(join(dirname(__file__), "rpg.schematron"))
    schematron_doc = etree.parse(schematron_fname)
    schematron_validator = Schematron(schematron_doc, store_report=True)
    return schematron_validator


xml_schema = load_xsd_schema()
schematron_validator = load_schematron_validator()


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


def split_ability_tokens(xml_str):
    """
    Extracts special ability tokens, e.g. ✱dagger.strike_1 from other text.

    """
    return _ability_tokenizer.split(xml_str)


def parse_xml_list(xml_node):
    """
    Parses xml like this: <xml_node> <A/> <B/><!-- a comment --><C/></xml_node>
    and returns a list like this: ["A", "B", "C"]

    """
    elements = []
    for child in list(xml_node):
        if child.tag is not COMMENT:
            elements.append(strip_xml(child.tag))
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


@lru_cache(maxsize=256)
def _get_defaults_tree(fname):
    """
    Method to get the defaults xml files and cache them because
    we don't want to do it over and over again when we don't need to.

    """
    if not fname.endswith(".xml"):
        fname += ".xml"
    full_fname = join(default_abilities_dir, fname)
    defaults_tree = etree.parse(full_fname)
    return defaults_tree


def _replace_xdefs(tree, source_fname):
    """
    Custom method that does kind of what xinclude is supposed to do.
    (XInclude looks like it's died at the spec level - in its current
    form it's semi-useless).

    """
    for xdef_elem in tree.iter("xdef"):
        fname = xdef_elem.get("fname", None)
        if fname is None:
            raise Exception(
                "Error can't replace <xdef/> element.  "
                "No 'fname' attribute specified in "
                f"file {source_fname} on line {xdef_elem.sourceline}")

        elem_name = xdef_elem.get("elem_name", None)
        if elem_name is None:
            raise Exception(
                "Error can't replace <xdef/> element. "
                "No elem_name attribute specified in "
                f"file {source_fname} on line {xdef_elem.sourceline}")

        # get the default element tree from the defaults file
        defaults_tree = _get_defaults_tree(fname)
        default_element = defaults_tree.find(f".//{elem_name}")

        # You can't substitute a default element in if that default element
        # does not exist.
        if default_element is None:
            raise Exception(
                f"Default element '{elem_name}' is not specified in "
                f"defaults file {fname}.  However it is referenced in "
                f"file {source_fname} on line {xdef_elem.sourceline}")

        # Create a copy of the defaul element.
        # (Deepcopy doesn't copy the sourceline value, strangely.  The
        # sourceline value will be the line number in the pre-replacement xml).
        new_element = deepcopy(default_element)
        new_element.sourceline = xdef_elem.sourceline

        # Replace the xdef element with the element copied from the
        # defaults file.
        xdef_elem.getparent().replace(xdef_elem, new_element)
    return


def perform_schematron_validation(fname, tree):
    validation_result = schematron_validator.validate(tree)
    if not validation_result:
        report = schematron_validator.validation_report
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
                    elements = tree.xpath(source_xpath)
                    message = contents_to_string(child)
                    if len(elements) != 1:
                        raise Exception("Unknown or missing elements")
                    element = elements[0]
                    print(f"Schematron error '{message} [{test}]' at "
                          f"{element.tag} in {fname}:{element.sourceline}")
                    print(get_error_context(fname, element.sourceline))

                # found something that may or may not be interesting.
                # needs further investigation so we can decide to log
                # or ignore it.
                case _:
                    raise Exception(f"UNKNOWN CHILD {child.__class__} {tag}")

        raise Exception(f"Schematron error!!!")
    return


def parse_xml(fname):
    try:
        # Parse the xml
        tree = etree.parse(fname)

        # Do some #include like substitution.
        # XInclude is an abortion.  We'll roll our own called <xdef>.
        _replace_xdefs(tree, fname)

        # Do some extra validation
        perform_schematron_validation(fname, tree)

    except lxml.etree.XMLSyntaxError as lxml_err:
        lxml_err.msg += " happens in file: %s" % fname
        line, column = lxml_err.position
        print(lxml_err)
        print(get_error_context(fname, line))
        tree = None

    except Exception as err:
        print(f"Problem parsing file: {fname}")
        raise
    return tree


def xml_tree_to_str(tree):
    """
    Pretty print xml tree for debugging.

    """
    xml_str = etree.tostring(tree, pretty_print=True)
    return xml_str.decode()


def validate_xml(doc):
    """
    Return a list (an iterable) of errors or None.

    """
    if not xml_schema.validate(doc):
        return xml_schema.error_log
    return None


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

    """
    return (node.text or "") + "".join(
        [etree.tostring(child, encoding="unicode")
         for child in node.iterchildren()])


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


def get_error_context(fname, error_line_number):
    """
    Returns the neighbouring lines around an xml error for debug context.

    """
    context = ""
    with open(fname, "r") as f:
        lines = f.readlines()
        from_line = max(error_line_number - 7, 0)
        to_line = min(error_line_number + 7, len(lines))
        for line_number in range(from_line, to_line):
            if line_number + 1 == error_line_number:
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
            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n"
                            (child.tag, fname, child.sourceline))
    return text_repr


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
