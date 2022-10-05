"""
 
  Utility methods.
  Hide lxml calls here.


"""
import sys
from os.path import abspath, join, dirname
import codecs
import lxml
# third party
from lxml import etree
COMMENT = etree.Comment
# local
from config import use_imperial

# directory constants
root_dir = abspath(join(dirname(__file__), ".."))
build_dir = join(root_dir, "build")
pdfs_dir = join(root_dir, "pdfs")
docs_dir = join(root_dir, "docs")
fonts_dir = join(root_dir, "fonts")
resources_dir = join(root_dir, "resources")
char_sheet_dir = join(resources_dir, "character_sheets")
archetypes_dir = join(root_dir, "archetypes")
ability_groups_dir = join(root_dir, "abilities")
encounters_dir = join(root_dir, "encounters")
modules_dir = join(root_dir, "modules")
styles_dir = join(root_dir, "styles").replace("\\", "/")


# load the xml schema
def load_schema(schema_fname):
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


schema_fname = abspath(join(dirname(__file__), "rpg.xsd"))
xml_schema = load_schema(schema_fname)



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


def parse_xml(fname):    
    try:
        result = etree.parse(fname)
    except lxml.etree.XMLSyntaxError as lxml_err:
        lxml_err.msg += " happens in file: %s" % fname
        line, column = lxml_err.position
        print(lxml_err)
        print(get_error_context(fname, line))        
        result = None

    except Exception as err:
        print(f"Problem parsing file: {fname}")
        raise
    return result


def validate_xml(doc):
    result = None
    if not xml_schema.validate(doc):
        result = "\n".join([str(e) for e in xml_schema.error_log])
    return result


def node_to_string(node):
    """
    Returns the nodes contents and its children as a string.

    """
    return etree.tostring(node, pretty_print=True, encoding="unicode")


def children_to_string(node):
    """
    Returns the nodes children as a string (just the xml elements).

    """
    return "".join([
        etree.tostring(c, pretty_print=True, encoding="unicode")
        for c in node.getchildren()
    ])
        

def contents_to_string(node):
    """
    Returns everything between the nodes tags <x>..</x> but NOT the tags themselves.

    """
    return (node.text or "") + "".join(
        [etree.tostring(child, encoding="unicode") for child in node.iterchildren()])


def contents_to_comma_separated_list(node):
    """
    Given <node><a/><b/><c/></node> returns a string a, b, c..

    """
    return (node.text or "") + ", ".join(
        [etree.tostring(child, encoding="unicode").strip()[1:-2] # remove < and />
         for child in node.iterchildren()])


def attrib_is_true(xml_node, attribute):
    """
    Returns True if the xml_node has the attribute specified and it's set to true.

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
    context = ""

    with open(fname, "r") as f:
        lines = f.readlines()            
        from_line = max(error_line_number - 5, 0)
        to_line = min(error_line_number + 5, len(lines))
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
    return ("0", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X")[number]


def convert_str_to_bool(str_bool):
    return str_bool.lower() != "false"


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
            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
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

