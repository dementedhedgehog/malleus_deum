"""
 
  Utility methods.
  Hide lxml calls here.


"""
import sys
from os.path import abspath, join, dirname
import codecs
import lxml
from lxml import etree


XSD_SCHEMA = abspath(join(dirname(__file__), "rpg.xsd"))
xml_schema_doc = etree.parse(XSD_SCHEMA)
xml_schema = etree.XMLSchema(xml_schema_doc)
xml_parser = etree.XMLParser(dtd_validation=True, attribute_defaults=True)

# directory constants
root_dir = abspath(join(dirname(__file__), ".."))
resources_dir = join(root_dir, "resources")
build_dir = join(root_dir, "build")
pdfs_dir = join(root_dir, "pdfs")
fonts_dir = join(root_dir, "fonts")
char_sheet_dir = join(resources_dir, "character_sheets")
archetypes_dir = join(root_dir, "archetypes")
ability_groups_dir = join(root_dir, "abilities")


from config import use_imperial
COMMENT = etree.Comment



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


def convert_to_roman_numerals(number):
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
        print "Problem in file: %s" % fname
        raise
    return result


def validate_xml(doc):
    result = None
    if not xml_schema.validate(doc):
        #result = xml_schema.error_log.last_error
        result = "\n".join([str(e) for e in xml_schema.error_log])
    return result


def get_error_context(fname, error_line_number):
    context = ""

    with file(fname, "r") as f:
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


def node_to_string(node):
    """
    Returns the nodes contents and its children as a string.

    """
    return etree.tostring(node, pretty_print=True)


def children_to_string(node):
    """
    Returns the nodes children as a string (just the xml elements).

    """
    return "".join([
        etree.tostring(c, pretty_print=True) for c in node.getchildren()
    ])
    

def contents_to_string(node):
    """
    Returns everything between the nodes tags <x>..</x> but NOT the tags themselves.

    """
    return (node.text or "") + "".join(
        [etree.tostring(child) for child in node.iterchildren()])
