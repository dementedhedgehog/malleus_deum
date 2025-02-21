#!/usr/bin/env python3
"""

  I was going to have ability ranks have their own settings for 
  checks and damage and promotions etc .. but that's way too
  complicated.  All that's move into Ability now so this code 
  is currently a mess.


"""
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
from os import listdir
from copy import copy
from collections import defaultdict

from utils import (
    parse_xml,
    validate_xml,
    get_error_context,
    node_to_string,
    COMMENT,
    children_to_string,
    convert_str_to_bool,
    contents_to_string,
    contents_to_comma_separated_str,
    contents_to_list,
    strip_xml,
    root_dir,
    src_dir,
    parse_xml_list,
)

from ability_check_defaults import AbilityCheckDefaultsLookup


def xor(a, b):
    return not b if a else bool(b)






MIN_INITIAL_ABILITY_RANK = -6
MAX_INITIAL_ABILITY_RANK = 3

# ability tags
ACCURATE = "Std+3×Rank"
INACCURATE_CHECK_TYPE = "Std"
MONSTER_CHECK_TYPE = "No-Check"
STD_CHECK = r"Std\+Rank"
UNTRAINED = "Untrained"
MAGIC_CHECK_TYPE = "Magic+Rank"
NO_CHECK = "no-check"

# A list of valid dcs
# We limit the range of values to reduce complexity in the system.  This should make 
# it easier to remember dcs?  We choose odd ddcs because 5 is the lowest dc you can
# fail at Rank 3.
DEFEND_DC = "Opponent's Attack DC"
GM_FIAT = "GM Fiat"

# FIXME: move into XML enum?
VALID_DCS = ("3", "5", "7", "9", "11", "13", "15", "17", "19", "21", "23", "25", "27", "29",
             "31", "33", "35", "37", "39",
             "GM Fiat",
             
             # for NPC/GM/Hazard abilities
             "9+Rank", "11+Rank", "13+Rank", "15+Rank",
             # Defend checks
             DEFEND_DC,
             # Save checks
             GM_FIAT,

             # 
             "Target's Defence", "Target's Attack", "Critical Success",
             "Target's Strength", "Target's Agility", "Target's Perception", "Target's Speed", "Target's Endurance",
             "Target's Agility or Speed",
             "Target's Mettle", "Target's Willpower",
             "Target's Negotiate or 11",
             "Target's Etiquette or 11",
             "Triggers Ability")


def is_valid_dc(rank):
    """
    Returns True if the rank is an acceptable rank.
    """
    return rank in VALID_DCS


# ability rank id -> ability rank lookup table
ability_rank_lookup = {}

# atributes
valid_attrs = ("Strength", "Endurance", "Agility", "Speed", "Perception")               
ATTRS = ("strength", "endurance", "agility", "speed", "perception")

# We use splines in the skill tree graphs
def parse_spline(point_nodes):
    points = []
    for point_node in point_nodes:
        x = float(point_node.attrib["x"])
        y = float(point_node.attrib["y"])
        points.append((x, y))
    return points


class ActionType:
    TAG = "Tag"

    # melee abilities
    IMMEDIATE = "Immediate"
    STANDARD = "Standard"
    MINOR = "Minor"
    MOVE = "Move"
    FREE = "free"
    REACTION = "Reaction"
    REACTION_OR_MINOR = "Reaction|Minor"
    NON_COMBAT = "Noncombat"
    FULL_TURN = "Full-Turn"
    MULTI_TURN = "Multi-Turn"
    
    @staticmethod
    def load(action_type_str):        
        if action_type_str == "<tag/>":
            action_type = ActionType.TAG
        elif action_type_str == "<immediate/>":
            action_type = ActionType.IMMEDIATE
        elif action_type_str == "<standard/>":
            action_type = ActionType.STANDARD
        elif action_type_str == "<minor/>":
            action_type = ActionType.MINOR
        elif action_type_str == "<move/>":
            action_type = ActionType.MOVE
        elif action_type_str == "<reaction/>":
            action_type = ActionType.REACTION
        elif action_type_str == "<noncombat/>":
            action_type = ActionType.NON_COMBAT
        elif action_type_str == "<full-turn/>":
            action_type = ActionType.FREE
        elif action_type_str == "<free/>":
            action_type = ActionType.FULL_TURN
        elif action_type_str == "<multi-turn/>":
            action_type = ActionType.MULTI_TURN
        elif action_type_str == "<reaction-or-minor/>":
            action_type = ActionType.REACTION_OR_MINOR
        else:
            raise Exception(f"Unknown action type: {action_type_str}")
        return action_type

    
class Prerequisite(object):
    def get_ability(self):
        return None


class AbilityRankPrereq(Prerequisite):

    def __init__(self, ability_rank_id):
        assert ability_rank_id is not None
        self.ability_rank_id = ability_rank_id
        self.ability_rank = None
        return

    def get_ability(self):
        ability_rank = self.get_ability_rank()
        if ability_rank is None:
            return None
        return ability_rank.ability

    def get_ability_rank(self):
        """Returns None if the rank does not exist!"""
        if self.ability_rank is None:
            self.ability_rank = ability_rank_lookup.get(self.ability_rank_id)
        return self.ability_rank
    
    def to_string(self):         
        return str(self.get_ability_rank())

    def get_ability_rank_id(self): 
        return self.ability_rank_id

    def get_title(self):
        return self.get_ability_rank().get_title()

    def __str__(self):
        return self.to_string()

    def get_rank_number(self):
        if self.ability_rank_id is not None:
            rank = int(self.ability_rank_id.split("_")[-1])
        else:
            rank = 0
        return rank


class Specialization:
    """An alternative ability rank"""

    def __init__(self, name, ability):
        self.name = name
        self.ability = ability

    def get_title(self):
        return self.name

    def get_rank_number(self):
        return 3 # for now

    def get_checks(self):
        return []

    def get_long_name(self):
        return (self.ability.get_id().split(".")[-1] + "." + self.name).lower()

    def get_very_long_name(self):
        return (self.ability.get_id() + "." + self.name).lower()


class AttrPrereq(Prerequisite):

    def __init__(self, attr, value):
        self.attr = attr
        self.value = value
        return

    @classmethod
    def parse_xml(cls, prereq_attr_node):
        """
        Return a list of prereq attrs.

        """
        prereqs = []
        
        for child in list(prereq_attr_node):
           tag = child.tag

           if tag is COMMENT:
               # ignore comments!
               pass

           elif tag in ATTRS:
               attr = tag
               value = int(child.text)
               prereqs.append(AttrPrereq(attr, value))
           
           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag,
                                                      rank.ability.fname))
        return prereqs
    
    def to_string(self):
        return "%s>%s" % (self.attr, self.value)

    def get_title(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()    

    
class TagPrereq(Prerequisite):
    """
    Tag prerequisites.

    """
    def __init__(self, tag):
        self.tag = tag
        return
    
    def to_string(self):
        return "Tag: %s" % self.tag

    def get_title(self):
        return self.tag

    def __str__(self):
        return self.to_string()


class NotTagPrereq(Prerequisite):

    def __init__(self, tag):
        self.tag = tag
        return
    
    def to_string(self):
        return "Not %s" % self.tag

    def get_title(self):
        return self.to_string()

    def __str__(self):
        return self.to_string()


class AbilityRank:
    """
    Every ability has a number of ranks, e.g. 1-6.

    """
    @classmethod
    def get_rank(cls, ability_rank_id):
        """
        Get the rank with the given id or None.

        """
        assert(ability_rank_id.__class__ is str)
        return ability_rank_lookup.get(ability_rank_id, None)

    def __init__(self):
        self.rank_number = None        
        self.ability = None

    def get_checks(self):
        return self.ability.get_checks()

    def get_ability(self):
        return self.ability

    def __str__(self):
        return self.get_title()

    def get_title(self, long_form=False):
        if long_form:
            str_template = "%s Rank: %s"
        else:
            str_template = "%s %s"
        return  str_template % (self.ability.get_title(), self.rank_number)

    def get_id(self):
        return "%s_%s" % (self.ability.get_id(), self.rank_number)

    def get_short_id(self):        
        return "%s_%s" % (self.ability.get_short_id(), self.rank_number)    

    def get_rank_number(self):
        return self.rank_number
    

class AbilityCheck:
    """
    An ability check configuration.

    """

    # The shared ability check defaults lookup table (lazy-load this)
    defaults_lookup = None

    @classmethod
    def load_ability_check_defaults(cls, ability_check_defaults_dir):
        if cls.defaults_lookup is None:
            cls.defaults_lookup = AbilityCheckDefaultsLookup()
            cls.defaults_lookup.load(ability_check_defaults_dir)
        return

    
    def __init__(self, ability):
        self.ability = ability

        # can be None for the default
        self.name = None
        self.ability_check_class = None
        self.dc = None
        self.action_type = None
        self.trigger = None        
        self.dmg = None
        self.effect = None

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

        # range of the attack/spell etc
        self.check_range = None

        # The check to use for saves
        self.save = None

        # what check is being rolled (for defence).

        # list of tags for the ability
        self.keywords = []

        # line number of the start of the ability check.
        self.line_number = None

        # some defaults values for this class of ability.
        self.defaults = None

    def get_name(self):
        return self.name
        
    def get_action_type(self):
        return self.action_type
        
    def get_keywords(self):
        return sorted(list(set(self.keywords + self.ability.get_keywords())))
        
    def get_range(self):
        return self.check_range        

    def get_damage(self):
        return self.dmg

    def get_trigger(self):
        return self.trigger

    def _load(self, ability_check_element):
        
        # handle all the children
        for child in list(ability_check_element):

            if self.line_number is None:
                self.line_number = child.sourceline
            
            tag = child.tag
            if tag == "name":
                self.name = contents_to_string(child)

            elif tag == "defaults":
                # set a bunch of default values to save on duplicated fields in checks
                defaults_name = contents_to_string(child)
                if defaults_name.strip() == "":
                    raise Exception(f"Ability has an empty <defaults> element on Line: {child.sourceline}")
                
                self.defaults = self.defaults_lookup.get(defaults_name)
                if self.defaults is None:
                    raise Exception("Can't find an ability check defaults "
                                    f"file named {defaults_name}")
                self.defaults.apply_defaults(self)

            # elif tag == "actiontype":
            #     self.action_type = contents_to_list(child).pop(0)

            # elif tag == "actiontype":
            #     action_type_str = contents_to_string(child)
            #     self.action_type = ActionType.load(action_type_str)            
            #     if self.action_type == None:
            #         raise Exception("Unknown action type: (%s) %s in %s\n" %
            #                         (child.tag, child.text, self.ability.fname))

            elif tag == "actiontype":
                self.action_type = contents_to_string(child) # FIXME: WHAT DO WE DO WITH THIS???
            
            elif tag == "trigger":
                self.trigger = contents_to_string(child)                

            elif tag == "range":
                self.check_range = contents_to_comma_separated_str(child)                

            # Mastery
            elif tag == "critsuccess":
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

            elif tag == "save":
                self.save = contents_to_string(child)

            elif tag == "dc":
                self.dc = contents_to_string(child)
                if not self.dc:
                    raise Exception(f"Ability is missing {self.ability_id} a dc "
                                    f"on line {child.line}"
                                    f"It should be one of {VALID_DCS}.")
                        
            elif tag == "dmg":
                self.dmg = contents_to_string(child)

            elif tag == "effect":
                self.effect = contents_to_string(child)

            elif tag == "range":
                self.ability_range = contents_to_string(child)

            elif tag == "keywords":
                self.keywords += parse_xml_list(child)

            elif tag is COMMENT:
                # ignore comments!
                pass

            else:
                raise Exception("UNKNOWN (%s) in file %s\n" % 
                                (child.tag, self.ability.fname))        
        return

    def __str__(self):
        return f"{self.name}: {self.dc} vs DC {self.dc}"

    def get_problems(self):
        problems = []

        if NO_CHECK in self.keywords:
            if self.dc is not None:
                problems.append(f"Ability {self.ability.ability_id} in "
                                f"{self.ability.fname}:{self.line_number} has a "
                                f"'no-check' keyword and a non-None dc: '{self.dc}'.\n")

        if self.dc and not is_valid_dc(self.dc):
            problems.append(f"Ability {self.ability.ability_id} in "
                            f"{self.ability.fname}:{self.line_number} has an "
                            f"invalid dc '{self.dc}'.  "
                            f"It should be one of {VALID_DCS}.\n")

        # Every check should have a check type (part of the action economy.. e.g. standard).
        if self.action_type is None:
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} has an "
                            f"invalid actiontype '{self.action_type}'.\n")

            
        if not self.name:
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} has a "
                            f"check without a name. "
                            "(The name element is required for all checks)!\n")
            
        if not self.check_range:
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} has a "
                            f"check without a range. "
                            "(The range element is required for all checks)!\n")
            

        #
        # Check the tags are set properly.
        #
        keywords = self.get_keywords()

        # Check that Defend checks are named Defend.
        if "defend" in keywords:
            if problem := self._check_name_if_keyword("defend", "Defend"):
                problems.append(problem)
        else:
            # Check that checks named Save have the save keyword
            if problem := self._check_name_if_keyword("save", "Save"):
                problems.append(problem)                

        # Normalize 'save' behaviour
        # Saves don't have these values.. they're determined by the opposed check.
        if problem := self._check_not_field_if_keyword("save", "critsuccess"):
            problems.append(problem)
        if problem := self._check_not_field_if_keyword("save", "righteoussuccess"):
            problems.append(problem)       
        if problem := self._check_not_field_if_keyword("save", "success"):
            problems.append(problem)       
        if problem := self._check_not_field_if_keyword("save", "fail"):
            problems.append(problem)       
        if problem := self._check_not_field_if_keyword("save", "grimfail"):
            problems.append(problem)
        if problem := self._check_not_field_if_keyword("save", "critfail"):
            problems.append(problem)
                
        # All defend checks are also save checks
        if "defend" in keywords and "save" not in keywords:
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} has a "
                            f"a 'defend' keyword (one of {keywords}) but does not have a 'save'"
                            "keyword.  (All defence checks are also save checks)!\n")
        
        # Can't have a pool based ability without a cost
        if self.is_pool_check() and not (self.indifferent or self.grimfail or self.critfail or
                                     self.success or self.righteoussuccess or self.critsuccess):
            problems.append(f"Ability {self.ability.title} in "
                            f"{self.ability.fname}:{self.line_number} uses "
                            f"a pool keyword (one of {keywords}) but has no pool cost "
                            "(If you have a pool then you muse lose pool points based on "
                            "the providence die result)!\n")

        # Saves shouldn't have a DC .. the opposed check should specify (or
        # the GM decides by fiat).

        # Defends have a standard DC
        if "defend" in keywords:
            if self.dc != DEFEND_DC:
                problem = self._create_problem(
                    "All checks with the 'defend' keyword *must* have the "
                    f" <dc> value set to `{DEFEND_DC}'.")
                problems.append(problem)
        elif "save" in keywords:
            if self.dc != GM_FIAT:
                problem = self._create_problem(
                    "All checks with the 'save' keyword and *not* the 'defend' keyword "
                    f"*must* have the <dc> value set to `{GM_FIAT}'.")
                problems.append(problem)
            
        # Must have a <range> element.
        if problem := self._check_field("check_range", "range"):
            problems.append(problem)

        if problem := self._check_name_if_keyword("opposed", "Opposed"):
            problems.append(problem)
            
        if problem := self._check_keyword_iff_field("opposed", "save"):
            problems.append(problem)

        if problem := self._check_field_if_keyword("opposed", "success"):
            problems.append(problem)

        if problem := self._check_field_if_keyword("opposed", "fail"):
            problems.append(problem)

        # FIXME: should we require crit values?
        if problem := self._check_not_field_if_keyword("opposed", "boon"):
            problems.append(problem)
        if problem := self._check_not_field_if_keyword("opposed", "bane"):
            problems.append(problem)

        
        
        # Check accurate tag
        # if xor(self.check_type == ACCURATE, "accurate" in tags):
        #     problems.append(f"Ability {self.ability.ability_id} is tagged accurate and does not "
        #                     f"have a {ACCURATE} check type, or vice versa")

        # Check inaccurate tag
        # if xor(self.action_type == INACCURATE_CHECK_TYPE, "inaccurate" in keywords):
        #     problems.append(f"Ability {self.ability.ability_id} is tagged inaccurate and does not "
        #                     f"have a {INACCURATE_CHECK_TYPE} check type {check_type} {keywords}, or vice versa")

        # # Check no-check std ability. (for monsters only)  
        # if self.check_type == MONSTER_CHECK_TYPE and "npc" not in keywords:
        #     problems.append(f"Ability {self.ability.ability_id} has a {MONSTER_CHECK_TYPE} check type but "
        #                     f"is not tagged with the npc tag.")

        # # Check ability ranks are sane
        # if len(self.ability.ranks) == 0:
        #     problems.append(f"Ability  {self.ability.ability_id} has no ability ranks set?")

        # # Check for untrained abilities.
        # elif UNTRAINED in keywords and self.ability.ranks[0].get_rank_number() >= 0:
        #     problems.append(f"Ability {self.ability.ability_id} is tagged 'Untrained' but does not "
        #                     f"have a negative ability rank")
            
        # check dcs are standard
        if self.dc in (STD_CHECK, ACCURATE) and self.dc not in ("3", "6", "9", "12", "15", "18", "21"):
            problems.append(f"Ability  {self.ability.ability_id} has a non-standard DC {self.dc} in "
                            f"{self.ability.fname}:{self.line_number}\n")

        # # magic checks have to have an overcharge
        # if self.check_type == MAGIC_CHECK_TYPE and self.overcharge is None:
        #     problems.append(f"Ability {self.ability.ability_id} is a magic check but has no overcharge")

        # # non-magic checks cannot have an overcharge
        # if self.check_type != MAGIC_CHECK_TYPE and self.overcharge is not None:
        #     problems.append(f"Ability {self.ability.ability_id} is not a magic check and has overcharge value")

        return problems

    def is_pool_check(self):
        keywords = self.get_keywords()
        for pool in ("magicpool", "mettlepool", "luckpool", "aspectpool"):
            if pool in keywords:
                return True
        return False


    def _create_problem(self, msg):
        """Helper to format xml configuration errors with some useful data."""
        return (f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} "
                f"{msg}\n")


    def _check_field(self, field_name, xml_element_name=None):
        field_value = getattr(self, field_name)
        if not field_value:
            name = xml_element_name if xml_element_name else field_name
            return self._create_problem(
                f"does not have a value for the {name} field set.\n")
        return None
    

    def _check_keyword_if_field(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if field_value and not keyword in keywords:
            return self._create_problem(
                f"has a value for the {field_name} set. but does not "                
                f" have the '{keyword}' keyword (one of {keywords})\n")
        return None
        

    def _check_field_if_keyword(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if keyword in keywords and not field_value:                    
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but does not "
                f"have a value for the {field_name} set.\n")
        return None
        
    def _check_not_field_if_keyword(self, keyword, field_name):
        keywords = self.get_keywords()
        field_value = getattr(self, field_name)
        if keyword in keywords and field_value:                    
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but "
                f"*has* a value for the {field_name} set.\n")
        return None
        

    def _check_keyword_iff_field(self, keyword, field_name):
        """Iff is shorthand for if-and-only-if"""
        if problem := self._check_keyword_if_field(keyword, field_name):
            return problem
        elif problem := self._check_field_if_keyword(keyword, field_name):
            return problem        
        return None
        
    def _check_name_if_keyword(self, keyword, check_name):
        keywords = self.get_keywords()
        if keyword in keywords and self.name != check_name:
            return (
                f"Ability {self.ability.title} in "
                f"{self.ability.fname}:{self.line_number} has "
                f"a '{keyword}' keyword (one of {keywords}) but does not "
                f"have a check name '{check_name}' (checks with a {keyword} "
                f"keyword must have the check name {check_name}).\n")
        return None
        



    
class Ability:
    """
    An ability.

    """
    # set of all ability ids we've seen there should be no duplicates!
    _ids = {}
    
    def __init__(self, fname, ability_group_id):
        self.fname = fname
        self.title = None
        self.ability_id = None
        self.description = None
        self.action_type = None
        self.specializations = []
        self.group_id = ability_group_id

        # checks .. a dictionary from name->check details.
        # an ability can have multiple check configurations
        self.checks = []
        
        # the check associated with this ability (Std, Magic, etc)
        self.check_type = None                 
        
        # prereq.
        self.ability_rank_prereq = None

        # all the prerequisites including the prereq_ability_rank
        self.prerequisites = []        

        # list of tags for the ability
        self.keywords = []

        # list of available ability ranks.
        self.ranks = []

        # list of specializations
        self.specializations = []

        # if this element is not none it should be a number in [-9, -6, -3, 0] the rank
        # at which untrained players make the check
        self.untrained_rank = None

        # list of spline points .. used for laying out the ability in a graph in the phb.
        self.spline = []

        # the group this ability belongs to.
        self.ability_group = None
        return

    def get_cost(self):
        return self.cost

    def get_action_type(self):
        return self.action_type

    # def get_range(self):
    #     return self.ability_range

    def get_keywords(self):
        return sorted(self.keywords + self.ability_group.get_keywords())

    def has_keywords(self):
        return len(self.get_keywords()) > 0

    def get_keywords_str(self):
        return ",".join(self.get_keywords())
    
    def __str__(self):
        return f"✱{self.ability_id}"

    def set_group(self, ability_group):
        self.ability_group = ability_group
            
    def get_group_id(self):
        return self.ability_group.get_id()

    def get_specializations_str(self):
        return ", ".join([s.name for s in self.specializations])
        
    # FIXME: what has this got to do with check_sanity?
    def get_problems(self):
        """Checks for malformed abilities.. returns a list of problems."""
        problems = []                
        
        if len(self.checks) == 0 and NO_CHECK not in self.get_keywords():
            problems.append(f"Ability {self.title} has no checks and does not have "
                            f"the <{NO_CHECK}/> keyword! {self.keywords}")
        else:
            for check in self.checks:
                problems += check.get_problems()

        # rank numbers can have an optional initial untrained/negative rank, after that the
        # should be a continuous range of increasing positive ints (or zero), e.g. -3, 0, 1, 2, 3
        # or 1, 2, 3, 4 are both valid.
        last_rank_number = None
        is_first_rank = True
        for ability_rank in self.get_trained_ranks():
            rank_number = ability_rank.get_rank_number()
                
            # check the first rank is always 0 or 1 (primary abilities can be lower).
            if is_first_rank:
                if ((rank_number < MIN_INITIAL_ABILITY_RANK or rank_number > MAX_INITIAL_ABILITY_RANK)
                    and "primary" not in self.keywords):
                    problems.append(
                        f"First rank for ability {self.get_title()} is {rank_number} "
                        f"should be {MIN_INITIAL_ABILITY_RANK} to {MAX_INITIAL_ABILITY_RANK}")
                is_first_rank = False
            else:
                if last_rank_number + 1 != rank_number:
                    problems.append("Bad rank numbers for ability %s around rank  %s"
                                    % (self.get_title(), rank_number))
            last_rank_number = rank_number
        return problems

    def get_trained_ranks(self):
        if self.is_untrained():
            if len(self.ranks) > 1:
                return self.ranks[1:]
            else:
                return []
        else:
            return self.ranks

    def check_sanity(self):
        problems = self.get_problems()
        if len(problems) > 0:
            raise Exception(", ".join([str(p) for p in problems]))
        return    

    def get_ability_rank_prereq(self):
        return self.ability_rank_prereq

    def is_valid_rank(self, rank):
        return int(rank) in self.ranks
    
    def get_ability_rank_range(self):
        trained_ranks = self.get_trained_ranks()
        first_ability_rank = trained_ranks[0].get_rank_number()
        last_ability_rank = trained_ranks[-1].get_rank_number()
        ability_ranks = f"{first_ability_rank}-{last_ability_rank}"
        return ability_ranks
    

    def is_core(self):  # FIXME: WHAT DOES THIS MEAN?
        return "core" in self.keywords

    def is_pool(self):
        return "pool" in self.keywords

    def get_rank_number(self):
        """
        Make ability look like ability rank so we can treat them the same-ish in other code
        (duck-typing ftw).

        """
        return None

    def get_name(self):
        """Return the abilities name."""
        return self.title
        
    def get_ability_rank(self, rank_number):
        for ability_rank in self.ranks:
            if ability_rank.get_rank_number() == rank_number:
                return ability_rank            
        return None

    def get_prerequisites_str(self):
        return ", ".join([str(p) for p in self.prerequisites])

    def get_attr_modifiers(self):
        return self.attr_modifiers

    def get_description(self):
        return self.description

    def get_ranks(self):
        return self.ranks

    def get_title(self):
        return self.title

    def get_check_type(self):
        return self.check_type
    
    def get_id(self):
        """Returns something like conjuration.ignis_2"""
        return self.ability_id

    # def get_short_id(self):
    #     """For conjuration.ignis_2 this will return the string ignis_2"""
    #     return self.ability_id.split(".")[-1]

    def get_checks(self):
        return self.checks
    
    def has_prerequisites(self):
        has_prereqs = False
        for rank in self.ranks:
            if rank.has_prerequisites():
                has_prereqs = True
                break
        return has_prereqs

    def __iter__(self):
        return iter(self.get_ranks())


    def load(self, ability_element):
        # check it's the right sort of element
        if ability_element.tag != "ability":
            raise Exception("UNKNOWN (%s) %s\n" % (ability_element.tag,
                                                   str(ability_element)))
        self._load(ability_element)
        return
    

    def _get_location(self, lxml_element):
        return "%s:%s" % (self.fname, lxml_element.sourceline)

    def _load(self, ability_element):
        # handle all the children
        for child in list(ability_element):            
            tag = child.tag
            if tag == "abilitytitle":
                if self.title is not None:
                    raise Exception("Only one abilitytitle per ability. (%s) %s\n" %
                                    (child.tag, str(child)))
                else:                   
                    self.title = child.text

            elif tag == "abilityid":
                if self.ability_id is not None:
                    raise Exception("Only one abilityid per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
                else:
                    # check for duplicates!
                    ability_id = child.text
                    ability_location = self._get_location(child)
                    if ability_id in self._ids:
                        raise Exception("Ability id: %s appears in two places %s and %s"
                                        % (ability_id,
                                           ability_location,
                                           self._ids[ability_id]))
                    else:
                        self._ids[ability_id] = ability_location
                        
                    # save the id!
                    self.ability_id = ability_id

            elif tag == "abilitycheck":
                ability_check = AbilityCheck(ability=self)
                ability_check._load(child)
                self.checks.append(ability_check)
                
            elif tag == "abilitygroup":
                self.group = contents_to_string(child)

            elif tag == "abilityactiontype":
                action_type_str = contents_to_string(child)
                self.action_type = ActionType.load(action_type_str)            
                if self.action_type == None:
                    raise Exception("Unknown action type: (%s) %s in %s\n" %
                                    (child.tag, child.text, self.fname))

            elif tag == "abilityranks":
                if len(self.ranks) > 0: #  is not None:
                    raise Exception("Only one abilityranks per ability. (%s) %s\n" %
                                    (child.tag, str(child)))
                else:
                    self.load_ability_ranks(child)

            elif tag == "abilitydescription":
                if self.description is not None:
                    raise Exception("Only one abilitydescription per ability. (%s) %s\n" %
                                    (child.tag, str(child)))
                else:
                    self.description = children_to_string(child)

            # elif tag == "specializations":
            #     if self.template is not None:
            #         raise Exception("Only one abilitytemplate per ability. (%s) %s\n" %
            #                         (child.tag, str(child)))
            #     else:
            #         self.template = child.text

            elif tag == "prereqabilityrank":
                ability_rank_id = child.text
                if ability_rank_id is not None:
                    prereq = AbilityRankPrereq(ability_rank_id)
                    self.ability_rank_prereq = prereq
                    self.prerequisites.append(prereq)

            elif tag == "prereqattr":
                prereqs = AttrPrereq.parse_xml(child)
                self.prerequisites += prereqs

            elif tag == "prereqtag":
                prerequisite_tag = child.text
                if prerequisite_tag is not None:
                    prereq = TagPrereq(prerequisite_tag)
                    self.prerequisites.append(prereq)

            elif tag == "prereqnottag":
                prerequisite_tag = child.text
                if prerequisite_tag is not None:
                    prereq = NotTagPrereq(prerequisite_tag)
                    self.prerequisites.append(prereq)

            elif tag == "keywords":
                self.keywords += parse_xml_list(child)

            elif tag == "spline":
                self.spline = parse_spline(child.getchildren())

            elif tag == "specializations":
                self.parse_specializations(child.getchildren())

            elif tag is COMMENT:
                # ignore comments!
                pass

            else:
                raise Exception("UNKNOWN (%s) in file %s\n" % 
                                (child.tag, self.fname))
        # sanity check.
        #self.validate()
        return


    def parse_specializations(self, specializations_element):
        """
        Parse a list of ability specializations from an xml specializations element.
        
        """
        for specialization_element in specializations_element:
            specialization_name = contents_to_string(specialization_element) # .lower()
            specialization = Specialization(name=specialization_name, ability=self)
            self.specializations.append(specialization)
            ability_rank_lookup[specialization.get_long_name()] = specialization
            ability_rank_lookup[specialization.get_very_long_name()] = specialization
        return

    
    # def is_gmg_ability(self):
    #     """
    #     Returns True if this is a special ability that should go in the GMG and not 
    #     in the PHB.

    #     """
    #     return self.gmg_ability

    def _add_ability_rank(self, rank_number):
        """Add an ability rank."""
        rank = AbilityRank()
        rank.ability = self
        rank.rank_number = rank_number

        # Store it twice .. once as ability_group.ability.rank
        # and once as ability.rank
        rank_id = rank.get_id()
        ability_rank_lookup[rank.get_id()] = rank

        #assert rank.get_short_id() not in ability_rank_lookup, f" --> {rank.get_id()} {rank.get_short_id()}"
        #if rank.get_short_id() in ability_rank_lookup:
        # if rank_id  in ability_rank_lookup:
        #     #raise Exception(f" --> {rank.get_id()}  {rank.get_short_id()}")
        #     raise Exception(f" --> {rank_id} ")
        # ability_rank_lookup[rank_id()] = rank
        self.ranks.append(rank)
        return
        
    def is_untrained(self):
        return self.untrained_rank is not None
    
    def get_untrained_rank(self):
        if self.untrained_rank is None:
            return None
        return self.ranks[0]
    
    def load_ability_ranks(self, ability_ranks):
        untrained_rank = ability_ranks.attrib.get("untrained", None)
        if untrained_rank is not None:
            self.untrained_rank = int(untrained_rank)
            self._add_ability_rank(self.untrained_rank)

        from_rank = int(ability_ranks.attrib["from"])
        to_rank = int(ability_ranks.attrib["to"])
        for rank_number in range(from_rank, to_rank+1):
            self._add_ability_rank(rank_number)
        return


class AbilityGroupInfo:
    """
    A group of abilities
    
    """
    # set of all ability ids we've seen
    # there should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.title = None
        self.ability_group_id = None
        self.description = None
        self.family_id = None
        self.keywords = []

        # Should we draw a skill tree when documenting the ability group?
        # (Some ability groups are very flat with no relationships)
        self.draw_skill_tree = True

        # Should this ability group be included in the docs?
        self.enabled = True
        return

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def load(self, ability_group_info_element):
        # check it's the right sort of element
        if ability_group_info_element.tag != "abilitygroupinfo":
            raise Exception("UNKNOWN (%s) %s\n" % (ability_group_info_element.tag,
                                                   str(ability_group_info_element)))
        self._load(ability_group_info_element)
        return

    def load_ability_keywords(self, ability_keywords_node):
        for child in list(ability_keywords_node):
            self.keywords.append(child.tag)
        return

    def _load(self, ability_group_info_element):
        # handle all the children
        for child in list(ability_group_info_element):
        
           tag = child.tag
           if tag == "abilitygrouptitle":
               if self.title is not None:
                   raise Exception("Only one abilitygrouptitle per file.")
               else:
                   self.title = child.text.strip()

           elif tag == "dontdrawskilltree":
               self.draw_skill_tree = False

           elif tag == "abilitygroupid":
               if self.ability_group_id is not None:
                   raise Exception("Only one abilitygroupid per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   group_ids = contents_to_list(child)
                   if len(group_ids) != 1:
                       raise Exception("Expecting 1 ability group id: got %s and %s"
                                       % (len(group_ids), contents_to_string(child)))
                       
                   ability_group_id = group_ids[0]
                   ability_group_location = "%s:%s" % (self.fname, child.sourceline)
                   if ability_group_id in self._ids:
                       previous_location = self._ids[ability_group_id]
                       raise Exception("Ability group id: '%s' appears in two places %s and %s"
                                       % (ability_group_id,
                                          ability_group_location,
                                          previous_location))
                   else:
                        self._ids[ability_group_id] = ability_group_location

                   # save the id!
                   self.ability_group_id = ability_group_id
                   
           elif tag == "abilitygroupfamily":
               if self.family_id is not None:
                   raise Exception("Only one abilitygroupfamily per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   family_ids = contents_to_list(child)
                   if len(family_ids) != 1:
                       raise Exception("Expecting 1 family id: got %s and %s"
                                       % (len(family_ids), contents_to_string(child)))
                   
                   # save the id location for debugging (can't have duplicates)!
                   #family_id = 
                   # family_id_location = "%s:%s" % (self.fname, child.sourceline)
                   # if family_id in self._ids:
                   #     previous_location = self._ids[ability_group_id]
                   #     raise Exception("Ability group id: '%s' appears in two places %s and %s"
                   #                     % (ability_group_id,
                   #                        ability_group_location,
                   #                        previous_location))
                   # else:
                   #      self._ids[ability_group_id] = ability_group_location

                   # save the id!
                   self.family_id = family_ids[0]
                   
                       
               #self.family_id = contents_to_string(child)
               #self.family_id = strip_xml(child)
               #assert self.family_id in FAMILY_TYPES, f"family {self.family} not in FAMILY_TYPES {FAMILY_TYPES}"

           elif tag == "keywords":
               self.load_ability_keywords(child)

           elif tag == "abilitygroupdescription":
               if self.description is not None:
                   raise Exception("Only one abilitygroupdescription per file.")
               else:
                   self.description = children_to_string(child)

           elif tag is COMMENT:
               pass # ignore comments!

           elif tag == "enabled":
               self.enabled = True

           elif tag == "disabled":
               self.enabled = False

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    def get_id(self):
        return self.ability_group_id


class AbilityGroup:
    xsd_schema = None

    def __init__(self, fname):
        self.fname = fname
        self.doc = parse_xml(fname)
        self.info = None
        self.abilities = []
        return

    def get_ability(self, ability_id):        
        for ability in self.abilities:
            if ability.ability_id == ability_id:
                return ability
        return None

    def get_keywords(self):
        return sorted(list(set(self.info.keywords + [self.info.family_id, self.info.ability_group_id])))

    def get_keywords_str(self):
        return ", ".join(self.get_keywords())

    def get_root_abilities(self):
        """
        Return a list of abilities that have no prerequisites.

        """
        root_abilities = []
        for ability in self.abilities:
            if ability.ability_rank_prereq is None:
                root_abilities.append(ability)

        return root_abilities

    def get_title(self):
        return self.info.title

    def get_abilities(self):
        return self.abilities

    def is_lore_family(self):
        return self.info.family_id == "lore"
    
    def is_general_family(self):
        return self.info.family_id == "general"
    
    def is_magic_family(self):
        return self.info.family_id == "magic"
    
    def is_martial_family(self):
        return self.info.family_id == "martial"

    def is_primary_family(self):
        return self.info.family_id == "primary"
    
    def is_common_family(self):
        return self.info.family_id == "common"

    def is_gm_family(self):
        return self.info.family_id == "gm"

    def is_wyrd_science_family(self):
        return self.info.family_id == "wyrd_science"

    def validate(self):
        """
        Returns None or a list of errors

        """
        return validate_xml(self.doc)

    def get_family(self):
        return self.info.family_id
    
    def __iter__(self):
        return iter(self.abilities)

    def get_id(self):
        return self.info.ability_group_id

    def get_info(self):
        return self.info

    def get_title(self):
        return self.info.get_title()

    def get_description(self):
        return self.info.get_description()
    
    def get_abilities(self):
        return self.abilities

    def has_abilities(self):
        return len(self.abilities) != 0

    def __cmp__(self, other):
        return cmp(self.get_title(), other.get_title())

    def __lt__(self, other):
        return self.get_title()  < other.get_title()

    def load(self, node = None):
        if node is None:
            root = self.doc.getroot()
        else:
            root = node

        # check it's the right sort of element
        if root.tag != "abilitygroup":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))
        
        # handle all the children of the ability group
        for child in list(root):
        
           tag = child.tag
           if tag == "abilitygroupinfo":
               if self.info is not None:
                   raise Exception("Only one abilitygroupinfo per file.  Filename: {self.fname}")
               else:
                   self.info = AbilityGroupInfo(self.fname)
                   self.info.load(child)

           elif tag == "ability":
               ability = Ability(self.fname, ability_group_id=self.get_id())
               try:
                   ability.load(child)
               except Exception as e:
                    # Add some extra debug info if we can.
                    e.add_note(f"File name: {self.fname}")
                    raise
                   
               ability.set_group(self)
               self.abilities.append(ability)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    def get_rank(self):
        return self.info.rank

    def draw_skill_tree(self):
        return self.info.draw_skill_tree

    def get_problems(self):
        """
        Perform some sanity checks.

        """
        problems = []
        group_id = self.info.ability_group_id

        if "_" in group_id:
            problems.append(f"Group id {group_id} contains an underscore.  "
                            "Latex doesn't like underscores. "
                            "Use a hyphen instead.")
        return problems

    def check_sanity(self):
        problems = self.get_problems()
        if len(problems) > 0:
            raise Exception(", ".join([str(p) for p in problems]))
        return    
    

class AbilityGroups:
    """
    A list of all abilities.

    """
    def __init__(self):
        self.ability_groups = []

        # id -> ability, e.g. ✱primary.perception -> Perception Ability obj
        self.ability_lookup = {}
        return

    def get_abilities_children(self, ability):
        """
        Return a list of abilities that require this ability
        as a prerequisite.

        """
        children = []

        # Do it the hard way.
        found = None
        ability_id = ability.get_id()
        for group in self.ability_groups:
            ability = group.get_ability(ability_id)
            if ability is not None:
                for a2 in group:
                    if a2.ability_rank_prereq is not None:
                        ability_prereq = a2.ability_rank_prereq.get_ability()
                        if ability_prereq is None:
                            prereq_id = a2.ability_rank_prereq.get_ability_rank_id()
                            raise Exception(f"Ability prereq {prereq_id} does not exist for "
                                            f"ability: {ability.get_title()} {a2.get_title()}")
                        if ability_prereq == ability:
                            children.append(a2)
        return children                


    def __iter__(self):
        return iter(self.ability_groups)

    def get_ability_rank(self, ability_rank_id, rank=None):
        """

        Throws a key error if the rank is not found!
        """
        if ability_rank_id is None:
            return None
        if ability_rank_id.startswith("✱"):
            ability_rank_id = ability_rank_id[1:]
        if rank is not None:
            ability_rank_id = f"{ability_rank_id}_{rank}"
        #try:
        x = ability_rank_lookup[ability_rank_id]
        #except KeyError:
        #    for v in ability_rank_lookup.keys():
        #        print(v)
        #    print("Y2\n")
            
        return ability_rank_lookup[ability_rank_id]

    def get_abilities(self):
        for group in self.ability_groups:
            for ability in group.get_abilities():
                yield ability
        return        

    def get_abilities_by_family(self, family_type):
        abilities = []
        for ability_group in self.ability_groups:
            if ability_group.info.family_id == family_type:
                for ability in ability_group.get_abilities():
                    abilities.append(ability)
        abilities = sorted(abilities, key=lambda ability: ability.title)
        return abilities

    def get_abilities_by_family_paginated(self, family_type, page_size=30):
        abilities = self.get_abilities_by_family(family_type)
        return [abilities[i:i+page_size] for i in range(0, len(abilities), page_size)]
    
    def get_ability(self, ability_id):
        for group in self.ability_groups:
            ability =  group.get_ability(ability_id)
            if ability is not None:
                return ability
        return None

    def get_ability_group(self, ability_group_id):
        for group in self.ability_groups:
            if group.get_id() == ability_group_id:
                return group
        return None

    def load(self, abilities_dir, fail_fast):

        # Before we do anything load the default ability check classes.
        AbilityCheck.load_ability_check_defaults(abilities_dir)
        
        # load all the ability groups
        for xml_fname in listdir(abilities_dir):

            if not xml_fname.endswith(".xml"):
                continue

            if xml_fname.startswith(".#"):
                continue
            
            xml_fname = join(abilities_dir, xml_fname)
            ability_group = AbilityGroup(xml_fname)
            errors = ability_group.validate()
            if errors:
                if fail_fast:
                    for i, e in enumerate(errors):
                        print(f"error: {i}\n{str(e)}\n{ get_error_context(xml_fname, e.line) }\n\n")
                    raise Exception("Problem with xml %s" % xml_fname)
                else:
                    return False
            ability_group.load()

            self.ability_groups.append(ability_group)

            # populate the ability_id -> ability lookup table
            for ability in ability_group.get_abilities():
                self.ability_lookup[ability.get_id()] = ability

        # sort the groups
        self.ability_groups.sort()

        # die if anything is misconfigured.
        self.check_sanity()
        return True    

    def check_sanity(self):
        """
        Checks the "correctness" of the configuration.  Complains if it doesn't like it.

        """
        for ability_group in self:
            for ability in ability_group:
                ability.check_sanity()
                
            ability_group.check_sanity()
        return                        
    
    def get_ability_groups(self):
        return self.ability_groups
    
    def __getitem__(self, key):
        return self.ability_groups[key]

    


def get_ability_rank_total_prereqs(ability_groups, ability_rank, prereqs=None):
    """
    Gets a list of all the prereqs for this ability rank (including this ability rank).

    """
    if prereqs is None:
        prereqs = set()
    rank_number = ability_rank.get_rank_number()
    prereqs.add(ability_rank)
    
    ability = ability_rank.get_ability()
    for i in range(1, rank_number):
        pal = ability.get_ability_rank(i)
        get_ability_rank_total_prereqs(ability_groups,
                                        pal,
                                        prereqs=prereqs)
        
    for prereq in ability_rank.get_prerequisites():
        if isinstance(prereq, AbilityRankPrereq):
            prereq_ability_rank = ability_groups.get_ability_rank(prereq.ability_rank_id)
            get_ability_rank_total_prereqs(ability_groups,
                                            prereq_ability_rank,
                                            prereqs=prereqs)
    return prereqs
    

    
if __name__ == "__main__":

    # src_dir = abspath(join(dirname(__file__)))
    # root_dir = abspath(join(src_dir, ".."))
    #sys.path.append(src_dir)
    
    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast = True)
    
    build_dir = join(root_dir, "build")
    #ability_groups.draw_all_skill_trees(build_dir)
    #ability_groups.draw_skill_tree(build_dir)
    #ability_groups.draw_skill_tree2(build_dir)

    #ag = ability_groups.get_ability_group("primary")
    #ag = ability_groups.get_ability_group("transport")
    #print(ag.info.draw_skill_tree)

    # for ag in ability_groups:
    #     problems = ag.get_problems()
    #     print(", ".join(problems))
    
    #for ability in ag:
    #    print(f" {ability}  {ability.ability_id}")

    # for abilities_page in ability_groups.get_abilities_by_family_paginated("<primary/>"):
    #     print(abilities_page)
    #     count = 0
    #     for ability in abilities_page:
    #         count += 1
    #         print(f" {count} {ability.get_title()}")
    

    # count = 0
    # for ability_group in ability_groups:

    # #     if "Transport" not in ability_group.get_title():
    # #         continue

    #     print()
    #     print(ability_group.get_title())
        
    #     for ability in ability_group:            
    #         count += 1
    #         print("\t%i %s %s [%s] [%s]"
    #               % (count,
    #                  ability.get_title(),
    #                  ability.get_id(),
    #                  str(ability.get_untrained_rank()),
    #                  str(ability.untrained_rank)))
    #     #     # # print("\t\t\tAbility Class: %s" % ability.get_ability_class())
    #     #     # # print("\t\t\tAbility Desc: %s" % ability.description)
    #     #     # # #print("\t\t\tAbility Class: %s" % ability.get_ability_class())
    #     #     # # #print("\t\t\t\t: %s" % ability.get_ability_class())
            
    #     #     for ability_rank in ability.get_ranks():
    #     #         print("\t\t\t\t title %s" % ability_rank.get_title())
    #     #         print("\t\t\t\t prereqs %s" % ability_rank.get_prerequisites())

    #     #         pd = get_ability_rank_total_prereqs(ability_groups, ability_rank)
    #     #         #print("\t\t\t\t pd %s" % str(pd))
    #     #         print("\t\t\t\t pd %s" % ", ".join([p.get_title() for p in pd]))
                
    #     #     #     print("\t\t\t\t id %s" % ability_rank.get_id())
    #     #     # #     print("\t\t\t\t2 %s" % ability_rank.check)
    #     #     # #     print("\t\t\t\t3 %s" % ability_rank.description)
    #     #     # # #    #print("\t\t\tLore: %s" % ability_rank.get_default_lore())
            


    for k,v in ability_rank_lookup.items():
        print(f"{k} --> {v}")
