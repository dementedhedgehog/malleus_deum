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
    node_to_string,
    COMMENT,
    children_to_string,
    #convert_to_roman_numerals,
    convert_str_to_bool,
    contents_to_string,
)

src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
sys.path.append(src_dir)


def xor(a, b):
    return not b if a else bool(b)

# This is the high rank action tag for broad classification of skills.
class FAMILY_TYPE:
    LORE = "<lore/>"
    MARTIAL = "<martial/>"
    GENERAL = "<general/>"
    PRIMARY = "<primary/>"
    MAGICAL = "<magical/>"
    NPC = "<npc/>"
FAMILY_TYPES = ("<lore/>", "<martial/>", "<magical/>", "<general/>",  "<primary/>", "<npc/>")

MIN_INITIAL_ABILITY_RANK = 1
MAX_INITIAL_ABILITY_RANK = 1

# ability tags
ACCURATE = "Std+3×Rank"
INACCURATE_CHECK_TYPE = "Std"
MONSTER_CHECK_TYPE = "No-Check"
STD_CHECK = "Std\+Rank"
UNTRAINED = "Untrained"


class AbilityFamily:
    def __init__(self, family_type):
        self.family_type = family_type
        self.name = family_type[1:-2].title()

ability_families = [AbilityFamily(family_type) for family_type in FAMILY_TYPES]

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
    NON_COMBAT = "Non-Combat"
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
        elif action_type_str == "<non-combat/>":
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
        return self.get_ability_rank().ability

    def get_ability_rank(self):
        if self.ability_rank is None:
            self.ability_rank = ability_rank_lookup[self.ability_rank_id]
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
    Every ability has a number of ranks.

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

    def get_damage(self):
        return self.ability.get_damage()
    
    def get_ability(self):
        return self.ability

    def __str__(self):
        return self.get_title()

    def is_templated(self):
        return self.ability.is_templated()

    def get_template(self):
        return self.ability.get_template()
    
    def get_title(self):
        # rank_num = convert_to_roman_numerals(self.rank_number)
        # return "%s %s" % (self.ability.get_title(), rank_num)
        #rank_num = convert_to_roman_numerals(self.rank_number)
        return "%s %s" % (self.ability.get_title(), self.rank_number)

    def get_id(self):
        return "%s_%s" % (self.ability.get_id(), self.rank_number)

    def get_rank_number(self):
        return self.rank_number
    

class AbilityCheck:
    """
    An ability check configiuration.

    """

    def __init__(self, ability):
        self.ability = ability

        # can be None for the default
        self.name = None
        self.dc = None
        self.overcharge = None

    def _load(self, ability_check_element):
        self.name = ability_check_element.attrib.get("name", "Default")
        self.dc = ability_check_element.attrib.get("dc")
        self.overcharge = ability_check_element.attrib.get("overcharge")        
        return

    def __str__(self):
        if self.overcharge is not None:
            return f"{self.name}: {self.dc}/{self.overcharge}"
        return f"{self.name}: {self.dc}"

    def get_problems(self):
        problems = []
        check = self.name.casefold()
        looks_like_a_pool_check = "luck" in check or "mettle" in check or "magic" in check
        if looks_like_a_pool_check:
            if not self.is_pool():
                problems.append("Ability looks like a pool check but isn't tagged as such")

            if self.overcharge is None:
                problems.append("Ability looks like a pool check but doesn't have an overcharge")

            else:
                overcharge = self.overcharge.casefold()
                if "rank" not in overcharge:
                    problems.append("Ability looks like a pool check but rank "
                                    "doesn't modify the overcharge?")

            if "rank" in check:
                problems.append(f"Ability {self.ability.ability_id} looks like a pool check and "
                                "rank modifies the DC?")

        if not self.ability.is_pool() and self.overcharge is not None:
            problems.append(f"Ability  {self.ability.ability_id} looks like a std check and has an overcharge?")

        #
        # Check the tags are set properly.
        #
        tags = self.ability.get_tags()
        check_type = self.ability.get_check_type()

        # Check accurate tag
        if xor(check_type == ACCURATE, "accurate" in tags):
            problems.append(f"Ability {self.ability.ability_id} is tagged accurate and does not "
                            f"have a {ACCURATE} check type, or vice versa")

        # Check inaccurate tag
        if xor(check_type == INACCURATE_CHECK_TYPE, "inaccurate" in tags):
            problems.append(f"Ability {self.ability.ability_id} is tagged inaccurate and does not "
                            f"have a {INACCURATE_CHECK_TYPE} check type {check_type} {tags}, or vice versa")

        # Check no-check std ability. (for monsters only)  
        if check_type == MONSTER_CHECK_TYPE and "monster" not in tags:
            problems.append(f"Ability {self.ability.ability_id} has a {MONSTER_CHECK_TYPE} check type but "
                            "is not tagged with the monster tag.")

        # Check Std+Rank has no overcharge
        if check_type in (STD_CHECK, ACCURATE) and self.overcharge is not None:
            problems.append(f"Ability {self.ability.ability_id} has a standard check type and an "
                            f"overcharge '{self.overcharge}'")

        # Check ability ranks are sane
        if len(self.ability.ranks) == 0:
            problems.append(f"Ability  {self.ability.ability_id} has no ability ranks set?")

        # Check for untrained abilities.
        elif UNTRAINED in tags and self.ability.ranks[0].get_rank_number() >= 0:
            problems.append(f"Ability {self.ability.ability_id} is tagged 'Untrained' but does not "
                            f"have a negative ability rank")
            
        # check dcs are standard
        if check in (STD_CHECK, ACCURATE) and self.dc not in ("3", "6", "9", "12", "15", "18", "21"):
            problems.append(f"Ability  {self.ability.ability_id} has a non-standard DC {self.dc}")

        return problems

    
class Ability:
    """
    An ability.

    """
    # set of all ability ids we've seen there should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.title = None
        self.ability_id = None
        self.description = None
        self.action_type = None
        self.template = None # for templated abilities this is the name of the template.

        # checks .. a dictionary from name->check details.
        # an ability can have multiple check configurations
        self.checks = {}
        
        # the check associated with this ability (Std, Magic, etc)
        self.check_type = None                 
        
        # the check associated with this ability
        self.damage = None
        
        # prereq.
        self.ability_rank_prereq = None

        # all the prerequisites
        self.prerequisites = []        

        # list of tags for the ability
        self.tags = []

        # If this is true put the ability in the GMG otherwise put it in
        # the players handbook
        self.gmg_ability = False        

        # list of ability ranks. positive ints.
        self.ranks = []

        # if this element is not none it should be a number in -9 to 0.. the rank
        # at which untrained players make the check
        self.untrained_rank = None

        # list of spline points
        self.spline = []
        return
            

    # FIXME: what has this got to do whith check_sanity?
    def get_problems(self):
        """Checks for malformed abilities.. returns a list of problems."""
        problems = []                
        
        if len(self.checks) == 0:
            problems.append("Ability has no checks!")
        else:
            for check in self.checks.values():
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
                    and "physical" not in self.tags):
                    problems.append(
                        f"First rank for ability {self.get_title()} is {rank_number} "
                        f"should be {MIN_INITIAL_ABILITY_RANK} to {MAX_INITIAL_ABILITY_RANK+1}")
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

    def get_damage(self):
        return self.damage if self.damage is not None else ""
    
    def get_ability_rank_range(self):
        first_ability_rank = self.ranks[0].get_rank_number()
        last_ability_rank = self.ranks[-1].get_rank_number()
        untrained_rank = "N/A" if self.untrained_rank is None else str(self.untrained_rank)
        return f"untrained: {untrained_rank} {first_ability_rank}-{last_ability_rank}"

    def is_core(self):
        return "core" in self.tags

    def is_pool(self):
        return "pool" in self.tags

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

    def get_tags(self):
        return self.tags

    def get_tags_str(self):
        return [",".join(self.get_tags())]

    def has_tags(self):
        return len(self.tags) > 0

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

    def is_templated(self):
        """Is this a templated ability?"""
        return self.template is not None

    def get_template(self):
        return self.template
    
    def get_id(self):
        return self.ability_id

    def get_checks(self):
        return self.checks.values()
    
    def has_prerequisites(self):
        has_prereqs = False
        for rank in self.ranks:
            if rank.has_prerequisites():
                has_prereqs = True
                break
        return has_prereqs

    def __iter__(self):
        return iter(self.get_ranks())

    def has_tags(self):
        return len(self.tags) > 0

    def get_tags_str(self):
        return ", ".join(self.tags)


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
               self.checks[ability_check.name] = ability_check

           elif tag == "abilitychecktype":
               if self.check_type is not None:
                   raise Exception("Only one abilitycheck per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.check_type = child.text

           elif tag == "gmgability":
                self.gmg_ability = True

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

           elif tag == "abilityddc":
               if self.ddc is not None:
                   raise Exception("Only one abilityddc per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.ddc = child.text.strip() if child.text is not None else None

           elif tag == "abilitydmg":
               if self.damage is not None:
                   raise Exception("Only one abilitydmg per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.damage = child.text.strip() if child.text is not None else None

           elif tag == "abilityovercharge":
               if self.overcharge is not None:
                   raise Exception("Only one abilityovercharge per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.overcharge = child.text.strip() if child.text else None

           # elif tag == "abilitymastery":
           #     if self.mastery is not None:
           #         raise Exception("Only one abilitymastery per ability. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.mastery = int(child.text.strip())

           elif tag == "abilitydescription":
               if self.description is not None:
                   raise Exception("Only one abilitydescription per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.description = children_to_string(child)

           elif tag == "abilitytemplate":
               if self.template is not None:
                   raise Exception("Only one abilitytemplate per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.template = child.text

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
               
           elif tag == "tags":
               self.parse_tags(child)

           elif tag == "spline":
               self.spline = parse_spline(child.getchildren())
               
           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN (%s) in file %s\n" % 
                               (child.tag, self.fname))
        # sanity check.
        #self.validate()
        return

    def parse_tags(self, tags_node):
        for child in list(tags_node):
            if child.tag is not COMMENT:
                tag = child.tag[1:-2]
                self.tags.append(child.tag)
        return
    
    def is_gmg_ability(self):
        """
        Returns True if this is a special ability that should go in the GMG and not 
        in the PHB.

        """
        return self.gmg_ability


    def _add_ability_rank(self, rank_number):
        """Add an ability rank."""
        rank = AbilityRank()
        rank.ability = self
        rank.rank_number = rank_number            
        ability_rank_lookup[rank.get_id()] = rank
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
        self.family = None # one of Combat, Mundane or Magic.
        self.tags = []

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


    def load_ability_tags(self, ability_tags_node):
        for child in list(ability_tags_node):
            self.tags.append(child.tag)
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
                   ability_group_id = child.text
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
               self.family = contents_to_string(child)
               assert self.family in FAMILY_TYPES, f"family {self.family} not in FAMILY_TYPES {FAMILY_TYPES}"

           elif tag == "abilitytags":
               self.load_ability_tags(child)

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
        return self.info.family == FAMILY_TYPE.LORE
    
    def is_general_family(self):
        return self.info.family == FAMILY_TYPE.GENERAL
    
    def is_magic_family(self):
        return self.info.family == FAMILY_TYPE.MAGICAL
    
    def is_martial_family(self):
        return self.info.family == FAMILY_TYPE.MARTIAL

    def is_primary_family(self):
        return self.info.family == FAMILY_TYPE.PRIMARY

    def is_npc_family(self):
        return self.info.family == FAMILY_TYPE.NPC

    def validate(self):
        valid = True
        error_log = validate_xml(self.doc)
        if error_log is not None:
            print("Errors (XSD)!")
            valid = False
            print("\t%s" % error_log)
        return valid

    def get_family(self):
        return self.info.family
    
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
                   raise Exception("Only one abilitygroupinfo per file.")
               else:
                   self.info = AbilityGroupInfo(self.fname)
                   self.info.load(child)

           elif tag == "ability":
               ability = Ability(self.fname)
               ability.load(child)
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

class AbilityGroups:
    """
    A list of all abilities.

    """
    def __init__(self):
        self.ability_groups = []
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
            a1 = group.get_ability(ability_id)
            if a1 is not None:
                for a2 in group:
                    if a2.ability_rank_prereq is not None:
                        ability_prereq = a2.ability_rank_prereq.get_ability()
                        if ability_prereq == ability:
                            children.append(a2)
        return children                


    def __iter__(self):
        return iter(self.ability_groups)

    def get_ability_rank(self, ability_rank_id):
        return ability_rank_lookup[ability_rank_id]

    def get_abilities(self):
        for group in self.ability_groups:
            for ability in group.get_abilities():
                yield ability
        return        

    def get_abilities_by_family(self, family_type):
        abilities = []
        for ability_group in self.ability_groups:
            if ability_group.info.family == family_type:
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
        
        # load all the ability groups
        for xml_fname in listdir(abilities_dir):

            if not xml_fname.endswith(".xml"):
                continue

            if xml_fname.startswith(".#"):
                continue
            
            xml_fname = join(abilities_dir, xml_fname)
            ability_group = AbilityGroup(xml_fname)
            if not ability_group.validate():
                if fail_fast:
                    raise Exception("Problem with xml %s" % xml_fname)
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
        for ability_group in self:
            for ability in ability_group:
                ability.check_sanity()
        return                        
    
    def get_ability_rank(self, ability_rank_id):
        return ability_rank_lookup[ability_rank_id]

    def get_ability_groups(self):
        return self.ability_groups
    
    def __getitem__(self, key):
        return self.ability_groups[key]


def get_ability_rank_total_prereqs(ability_groups, ability_rank, prereqs=None):
    """
    Gets a list of all the prereqs for this ability rank (including this ability rank.

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

    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast = True)
    
    build_dir = join(root_dir, "build")
    #ability_groups.draw_all_skill_trees(build_dir)
    #ability_groups.draw_skill_tree(build_dir)
    #ability_groups.draw_skill_tree2(build_dir)

    #ag = ability_groups.get_ability_group("primary")
    ag = ability_groups.get_ability_group("transport")
    #print(ag.info.draw_skill_tree)

    for ability in ag:
        print(f" {ability}  {ability.ability_id}")

    # for abilities_page in ability_groups.get_abilities_by_family_paginated("<primary/>"):
    #     print(abilities_page)
    #     count = 0
    #     for ability in abilities_page:
    #         count += 1
    #         print(f" {count} {ability.get_title()}")
    
    
    # for ability_group in ability_groups:

    #     if "Transport" not in ability_group.get_title():
    #         continue

    #     # print()
    #     # print(ability_group.get_title())
    #     # print(f"lore? {ability_group.is_lore_family()}")
    #     # print(f"magic? {ability_group.is_magic_family()}")
    #     # print(f"martial {ability_group.is_martial_family()}")
    #     # print(f"general {ability_group.is_general_family()}")
        
    #     for ability in ability_group:            
    #         #     count += 1
    #         print("\t%i %s %s %s"
    #               % (count,
    #                  ability.get_title(),
    #                  ability.get_id())
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
            


