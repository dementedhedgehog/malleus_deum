"""

   Ability Check Classes are a bundle of default values for common check types.
   The aim is to save a lot of duplication when writing up standard/common checks.

"""
from os import listdir
from os.path import join, splitext, basename

from utils import (
    parse_xml,
    validate_xml,
    get_error_context,
    COMMENT,
    contents_to_string,
    contents_to_comma_separated_str,
    contents_to_list,
    parse_xml_list,
    )




class AbilityCheckDefaults:
    """
    A set of default values to share amongst groups of ability checks.

    """
    def __init__(self, fname):

        # full xml path e.g. /home/blaize/proj/malleus_deum/abilities/ability_check_defaults/melee.xml
        self.fname = fname
        # file basename.. used as the key for the defaults, e.g. melee for the above example  
        self.name, _ = splitext(basename(fname))
        # the xml root element returned by lxml
        self.doc = parse_xml(fname)
        
        # Mastery
        self.critsuccess = None
        self.righteoussuccess = None
        self.success = None
        self.fail = None
        self.grimfail = None
        self.critfail = None

        # Fate
        self.blessed = None
        self.boon = None
        self.indifferent = None
        self.bane = None
        self.damned = None

        # Misc
        self.save = None
        self.dc = None
        self.action_type = None        
        self.check_range = None
        self.dmg = None
        

        # list of tags for the ability
        self.keywords = []        
        return

    
    def apply_defaults(self, ability_check):
        """
        Apply defaults to an ability check.

        """
        if self.critsuccess: ability_check.critsuccess = self.critsuccess
        if self.righteoussuccess: ability_check.righteoussuccess = self.righteoussuccess
        if self.success: ability_check.success = self.success
        if self.fail: ability_check.fail = self.fail
        if self.grimfail: ability_check.grimfail = self.grimfail
        if self.critfail: ability_check.critfail = self.critfail
        
        if self.blessed: ability_check.blessed = self.blessed
        if self.boon: ability_check.boon = self.boon
        if self.indifferent: ability_check.indifferent = self.indifferent
        if self.bane: ability_check.bane = self.bane
        if self.damned: ability_check.damned = self.damned

        if self.save: ability_check.save = self.save
        if self.dc: ability_check.dc = self.dc
        if self.dmg: ability_check.dmg = self.dmg
        if self.action_type: ability_check.action_type = self.action_type
        if self.check_range: ability_check.check_range = self.check_range
        ability_check.keywords.extend(self.keywords) 
        return
    
    def validate(self):
        """
        Returns None or a list of errors

        """
        return validate_xml(self.doc)

    def load(self):
        """
        Load the ability check class from an xml file.

        """
        ability_check_defaults = self.doc.getroot()

        # check it's the right sort of element
        if ability_check_defaults.tag != "abilitycheckdefaults":
            raise Exception("UNKNOWN (%s) %s\n" % (
                ability_check_defaults.tag,
                str(ability_check__class)))
        
        for child in list(ability_check_defaults):            
            tag = child.tag

            # print(tag)

            # Mastery
            if tag == "critsuccess":
                self.critsuccess = contents_to_string(child)

            elif tag == "righteoussuccess":
                self.righteoussuccess = contents_to_string(child)

            elif tag == "success":
                self.success = contents_to_string(child)

            elif tag == "fail":
                self.fail = contents_to_string(child)

            elif tag == "grimfail":
                self.grimfail = contents_to_string(child)

            elif tag == "critfail":
                self.critfail = contents_to_string(child)
                
            # Fate
            elif tag == "blessed":
                self.blessed = contents_to_string(child)

            elif tag == "boon":
                self.boon = contents_to_string(child)

            elif tag == "indifferent":
                self.indifferent = contents_to_string(child)

            elif tag == "bane":
                self.bane = contents_to_string(child)

            elif tag == "damned":
                self.damned = contents_to_string(child)

            # Misc..
            elif tag == "actiontype":
                self.action_type = contents_to_list(child).pop(0)                

            elif tag == "save":
                self.save = contents_to_string(child)

            elif tag == "dc":
                self.dc = contents_to_string(child)

            elif tag == "dmg":
                self.dmg = contents_to_string(child)

            elif tag == "range":
                self.check_range = contents_to_comma_separated_str(child)                
                
            elif tag == "keywords":
                self.keywords += parse_xml_list(child)

            elif tag is COMMENT:
                # ignore comments!
                pass

            else:
                raise Exception("UNKNOWN (%s) in file %s\n" % 
                                (child.tag, self.fname))
        return

    

class AbilityCheckDefaultsLookup:
    """
    A collection of Ability Check Defaults.

    """

    def __init__(self):
        # dictionary of name->ability_check_defaults
        self.lookup = {}
        return


    def load(self, abilities_dir, fail_fast=True):
        """
        Load all the xml files containing ability check defaults.

        """
        ability_check_defaults_dir = join(abilities_dir, "ability_check_defaults")
        
        for xml_fname in listdir(ability_check_defaults_dir):
            
            # only interested in xml files.
            if not xml_fname.endswith(".xml"):
                continue

            # not interested in temporary emacs files.
            if xml_fname.startswith(".#"):
                continue

            # read and parse the ability-check-defaults xml
            xml_full_fname = join(ability_check_defaults_dir, xml_fname)
            ability_check_defaults = AbilityCheckDefaults(xml_full_fname)
            errors = ability_check_defaults.validate()
            if errors:
                if fail_fast:
                    for i, e in enumerate(errors):
                        print(f"error: {i}\n{str(e)}\n{ get_error_context(xml_full_fname, e.line) }\n\n")
                    raise Exception("Problem with xml %s" % xml_full_fname)
                else:
                    return False
            ability_check_defaults.load()

            # add the ability check class to the lookup table.
            self.lookup[ability_check_defaults.name] = ability_check_defaults

            # if ability_check_defaults.name == "elemental_defaults":
            #     print(ability_check_defaults.name)
            #     print(ability_check_defaults.dc)
            #     sys.exit()
        return
            

    def get(self, ability_check_defaults_name):
        """
        Return the ability check class with the given name, or None if we can't find one with that name.

        """
        return self.lookup.get(ability_check_defaults_name)

    
    def __str__(self):
        return ',\n'.join([f"{k}: {v}" for (k, v) in self.lookup.items()])
