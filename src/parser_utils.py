"""

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
        result = xml_schema.error_log.last_error
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



COMMENT = etree.Comment


def node_to_string(node):
    """
    Returns the nodes contents and its children as a string.

    """
    return etree.tostring(node, pretty_print=True)


# def node_contto_string(node):
#     """
#     Returns the nodes contents and its children as a string.

#     """
#     return etree.tostring(node, pretty_print=True)


# def get_all_text(node):
#     """
#     Return all the text between <x>.. and.. </x> including <x> and </x>

#     """
#     return node_to_string(node, method = "xml")    


def children_to_string(node):
    """
    Returns the nodes children as a string.

    """
    return "".join([
        etree.tostring(c, pretty_print=True) for c in node.getchildren()
    ])
    
# def get_node_text(node):
#     retuirn 
#     # return (node.text or "") + "".join(
#     #     [child_to_string(child) for child in node.iterchildren()])

