#!/usr/bin/env python3
"""
   Reads the rpg.xsd schema in order to expose various constants in
   the schema to python and jinja as constants.

   Don't repeat yourselves (DRY)!

"""
import functools
import lxml
import utils
import re

_xml_namespace_regex = re.compile(r"\{.*?\}")
def _strip_schema_from_tag(tag):
    """
    Remove the namespace from xml elements
    e.g. tags look something like this:
       "{http://www.w3.org/2001/XMLSchema}element"    
    and we remove the namespace; everthing in {braces}.
    """    
    return _xml_namespace_regex.sub("", tag)


def _sanitize_name(prefix, name, suffix):
    """
    We want to convert name strings in xml to valid python variable names.
    We want that conversion to be predictable so we know what the python
    constant name is for a given element name in the schema.

    """
    return prefix + name.upper().replace("-", "_") + suffix
    

class Constants:

    def __init__(self):
        # We inject this dictionary into the jinja namespace?
        self._constants = {}


    def _parse_keywords(self, prefix, element):
        for child in element.iter():

            # Ignore comments
            if utils.is_comment(child):
                continue

            tag = _strip_schema_from_tag(child.tag)
            if tag != "element":
                continue

            # Ids are for code (lower case with underscores)
            raw_id = child.attrib.get("name", None)
            sanitized_id = _sanitize_name(prefix, raw_id, "_ID")
            self._constants[sanitized_id] = raw_id

            # Values are human readable (capitalized with hyphens)
            name = child.attrib.get("fixed", None)
            sanitized_name = _sanitize_name(prefix, raw_id, "_NAME")
            self._constants[sanitized_name] = name
            
            
    def parse_schema(self):
        """
        Parse the schema. Extract the keyword constants.
        Expose them as a dictionary.

        """
        schema = lxml.etree.parse(utils.schema_fname)
        for element in schema.iter():
            name = element.attrib.get("name", None)            
            if name == "abilityFamilyKeywordEnum":
                self._parse_keywords("ABILITY_FAMILY_", element)
            elif name == "abilityGroupKeywordEnum":
                self._parse_keywords("ABILITY_GROUP_", element)
        return

    def __getattr__(self, name):
        """
        Expose the constants dict to Python.

        """
        return self._constants[name]

    @staticmethod    
    @functools.cache
    def get_constants():
        """
        Factory method.

        """
        constants = Constants()
        constants.parse_schema()
        return constants

if __name__ == "__main__":
    constants = Constants.get_constants()
    #print(constants._constants)
    print(constants.ABILITY_FAMILY_GENERAL)
