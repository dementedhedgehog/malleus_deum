#!/usr/bin/env python
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
from os import listdir

from utils import (
    parse_xml,
    validate_xml,
    node_to_string,
    COMMENT,
    children_to_string,
    convert_to_roman_numerals,
    convert_str_to_bool
)
        
src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
sys.path.append(src_dir)



# ability level id -> ability level lookup
ability_level_lookup = {}

valid_attrs = ("Strength", "Endurance", "Agility", "Speed",  
               "Luck", "Willpower", "Perception")



class Prerequisite(object):
    pass


class AbilityLevelPrereq(Prerequisite):

    def __init__(self, ability_level_id):
        assert ability_level_id is not None
        self.ability_level_id = ability_level_id
        self.ability_level = None
        return

    def get_ability(self):        
        return self.get_ability_level().ability

    def get_ability_level(self):
        if self.ability_level is None:
            self.ability_level = ability_level_lookup[self.ability_level_id]
        return self.ability_level
    
    def to_string(self):         
        return str(self.get_ability_level())

    def get_ability_level_id(self): 
        return self.ability_level_id

    def get_title(self):
        return self.get_ability_level().get_title()

    def __str__(self):
        return self.to_string()


class AttrPrereq(Prerequisite):

    def __init__(self, attr, value):
        self.attr = attr
        self.value = value
        return

    @classmethod
    def parse_xml(cls, prereq_attr_node):
        attr = None
        value = None
        
        for child in list(prereq_attr_node):
           tag = child.tag

           if tag == "attr":
               if attr is not None:
                   raise Exception("Only one attr per prereqattr. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   attr = child.text.strip()
                   if attr not in valid_attrs:
                       raise Exception("Received invalid attr. (%s) expecting "
                                       "one of %s\n" %
                                       (child.tag, ", ".join(valid_attrs)))
                   
           elif tag == "value":
               if value is not None:
                   raise Exception("Only one value per prereqattr. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   value = int(child.text)
                   
           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag,
                                                      level.ability.fname))
        return AttrPrereq(attr, value)

    
    def to_string(self):
        return "%s>%s" % (self.attr, self.value)

    def get_title(self):
        return self.to_string()


    def __str__(self):
        return self.to_string()
    
    
    
class TagPrereq(Prerequisite):

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



class AbilityLevel:

    @classmethod
    def get_level(cls, ability_level_id):
        """
        Get the level with the given id or None.

        """
        assert(ability_level_id.__class__ is str)
        return ability_level_lookup.get(ability_level_id, None)

    def __init__(self):
        self.level_number = None        
        self.default_martial = 0
        self.default_general = 0
        self.default_lore = 0
        self.default_magical = 0

        # the check associated with this ability
        self.check = None 
        
        # the damage associated with this ability.
        self.damage = None

        # the effect associated with this ability
        self.effect = None

        self.description = None
        self.ability = None

        # Check 
        self.overcharge = None        

        # Ability level ids for levels that are a prerequisite for
        # this level.
        self.ability_level_prereqs = []

        # attribute prerequisites (e.g. Str > 13)
        self.prerequisite_attr = []

        # a list of archetype tags that are prerequistes for this ability.
        self.prerequisite_tags = []

        # all the prerequisites
        self.prerequisites = []

        # abilities that require this ability level as a prerequisite
        self.dependent_ids = []

        # mastery
        self.successes = 0
        self.failures = 0
        self.attempts = 0
        return

    def get_ability(self):
        return self.ability

    def get_lore_points(self):
        return self.default_lore

    def get_martial_points(self):
        return self.default_martial
    
    def get_general_points(self):
        return self.default_general

    def get_magical_points(self):
        return self.default_magical

    def __str__(self):
        return self.get_title()

    def is_innate(self):
        return (
            self.level_number == 0 and
            self.default_martial == 0 and 
            self.default_general == 0 and 
            self.default_lore == 0 and 
            self.default_magical == 0)

    def get_default_cost(self):
        return (self.default_martial +
                self.default_general +
                self.default_lore + 
                self.default_magical)

    def get_check(self):
        return self.check

    def get_damage(self):
        return self.damage if self.damage is not None else ""

    def get_effect(self):
        return self.effect if self.effect is not None else ""
    
    def get_overcharge(self):
        return self.overcharge if self.overcharge is not None else ""
    
    def get_title(self):
        return "%s %s" % (
            self.ability.get_title(), convert_to_roman_numerals(self.level_number))

    def get_id(self):
        return "%s_%s" % (self.ability.get_id(), self.level_number)

    def has_description(self):
        return self.description is not None

    def get_description(self):
        return self.description

    def has_dependencies(self):
        """Returns true if this ability level has prerequisites."""
        return len(self.dependent_ids) > 0

    def add_dependency(self, ability_level_id):
        """Add an ability level id as a dependent of this ability level"""
        return self.dependent_ids.append(ability_level_id)

    def get_level_number(self):
        return self.level_number

    def get_dependencies(self):
        """
        Returns a list of ability levels that have this ability level as a prerequisite.

        """
        return [ ability_level_lookup[aid] for aid in self.dependent_ids ]
        
    def is_prerequisite(self):
        """Returns true if this is a prerequisite for some other ability level"""
        return len(self.dependent_ids) > 0

    def get_prerequisites(self):
        return self.prerequisites

    def get_prerequisite_tags(self):
        return self.prerequisite_tags    

    def get_default_martial(self):
        return self.default_martial

    def get_default_general(self):
        return self.default_general
    
    def get_default_lore(self):
        return self.default_lore

    def get_default_magical(self):
        return self.default_magical

    def is_masterable(self):
        return self.successes > 0 or self.failures > 0 or self.attempts > 0

    def get_mastery_successes(self):
        return self.successes

    def get_mastery_attempts(self):
        return self.attempts

    def get_mastery_failures(self):
        return self.failures

    def has_prerequisites(self):
        return self.prerequisites

    def get_ability_level_prereqs(self):
       return self.ability_level_prereqs

    def get_successes(self):    
        return self.successes

    def get_attempts(self):    
        return self.attempts

    def get_failures(self):
        return self.failures
    
    
    @classmethod
    def load_ability_level(cls, fname, ability, ability_level_element):
        level = cls()
        level.ability = ability        
        
        # handle all the children
        for child in list(ability_level_element):
           tag = child.tag

           if tag == "defaultlore":
               if level.default_lore != 0:
                   raise Exception("Only one defaultlore per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.default_lore = int(child.text)

           elif tag == "defaultmartial":
               if level.default_martial != 0:
                   raise Exception("Only one defaultmartial per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.default_martial = int(child.text)
                   
           elif tag == "defaultgeneral":
               if level.default_general != 0:
                   raise Exception("Only one defaultgeneral per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.default_general = int(child.text)

           elif tag == "defaultmagical":
               if level.default_magical != 0:
                   raise Exception("Only one defaultmagical per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.default_magical = int(child.text)

           elif tag == "successes":
               if level.successes > 0:
                   raise Exception("Only one successes per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   if child.text is not None:
                       level.successes = int(child.text)

           elif tag == "attempts":
               if level.attempts > 0:
                   raise Exception("Only one attempts per abilitylevel. (%s) %s "
                                   "in file %s\n" % (child.tag, str(child), fname))
               else:
                   if child.text is not None:
                       level.attempts = int(child.text)

           elif tag == "failures":
               if level.failures > 0:
                   raise Exception("Only one masteryfailures per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   if child.text is not None:
                       level.failures = int(child.text)

           elif tag == "check":
               if level.check is not None:
                   raise Exception("Only one check per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   #level.check = get_text(child)
                   #level.check = node_to_string(child)
                   level.check = child.text

           elif tag == "damage":
               if level.damage is not None:
                   raise Exception("At most one damage per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.damage = child.text

           elif tag == "effect":
               if level.effect is not None:
                   raise Exception("At most one effect per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.effect = child.text
                   
           elif tag == "levelnumber":
               if level.level_number is not None:
                   raise Exception("Only one levelnumber per abilitylevel. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.level_number = int(child.text)

           elif tag == "leveldescription":
               if level.description is not None:
                   raise Exception("Only one description per ability-level. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   level.description = children_to_string(child)

           elif tag == "prereqabilitylevel":

               ability_level_id = child.text
               if ability_level_id is not None:
                   prereq = AbilityLevelPrereq(ability_level_id)                   
                   level.ability_level_prereqs.append(prereq)
                   level.prerequisites.append(prereq)

           elif tag == "prereqtag":
               prerequisite_tag = child.text
               if prerequisite_tag is not None:
                   prereq = TagPrereq(prerequisite_tag)
                   level.prerequisite_tags.append(prereq)
                   level.prerequisites.append(prereq)

           elif tag == "prereqnottag":
               prerequisite_tag = child.text
               if prerequisite_tag is not None:
                   prereq = NotTagPrereq(prerequisite_tag)
                   level.prerequisite_tags.append(prereq)
                   level.prerequisites.append(prereq)
                   
           elif tag == "prereqattr":
               prereq = AttrPrereq.parse_xml(child)
               level.prerequisite_attr.append(prereq)
               level.prerequisites.append(prereq)

           elif tag == "overcharge":
               overcharge = child.text.strip()
               if overcharge != "":
                   level.overcharge = overcharge
                   
           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag,
                                                      level.ability.fname))

        # add this ability level to the lookup table 
        # (after we have an id)
        ability_level_lookup[level.get_id()] = level

        # sanity checks
        if (level.get_level_number() > 0 and
            level.get_default_cost() == 0 and
            len(level.prerequisite_tags) == 0 and
            not level.get_ability().is_inborn()):
            raise Exception("Ability level %s has a level > 0 and 0 points cost.  "
                            "This is not allowed.  Non-zero ability levels must cost "
                            ">0 points to acquire by default (This can be modified by "
                            "archetypes down to zero) in %s." % 
                            (level.get_title(), basename(level.ability.fname)))

        elif level.get_level_number() == 0 and level.get_default_cost() != 0:
            raise Exception("Ability level %s has a level of 0 and > 0 points cost."
                            "This is not allowed.  Zero ability levels must cost "
                            "0 points to acquire by default in %s." % 
                            (level.get_title(), basename(level.ability.fname)))


        non_zero_skill_point_count = 0
        if level.default_martial > 0:
            non_zero_skill_point_count += 1

        if level.default_general > 0:
            non_zero_skill_point_count += 1
            
        if level.default_lore > 0:
            non_zero_skill_point_count += 1
            
        if level.default_magical > 0:
            non_zero_skill_point_count += 1

        if non_zero_skill_point_count > 1:
            raise Exception("Ability level %s costs two different types of skill points "
                            "This is not allowed in %s." % 
                            (level.get_title(), basename(level.ability.fname)))        

        # check that if an ability requires successes or failures it has check
        if ((level.successes > 0 or level.attempts > 0 or level.failures > 0)
            and
            (level.check is None or level.check.strip() == "")):
            raise Exception("Ability level %s (%s) requires mastery to level up but has "
                            "no check." % (level.get_title(), level.get_id()))
        return level


class AbilityClass:
    NONE = "None"

    # melee abilities
    AMBUSH = "Ambush"
    SURPRISE = "Surprise"
    INITIATIVE = "Initiative"
    TALK = "Talk"
    FIGHT_REACH = "Fight-Reach"
    START = "Start"
    FAST = "Fast"
    MEDIUM = "Medium"
    MEDIUM_OR_SLOW = "MediumOrSlow"
    START_AND_REACTION = "StartAndReaction"
    SLOW = "Slow"
    RESOLUTION = "Resolution"
    REACTION = "Reaction"
    NON_COMBAT = "Non-Combat"

    # misc abilities
    #LORE = "Lore"

    @classmethod
    def to_string(cls, ability_class):
        if ability_class is None:
            return AbilityClass.NONE
        return cls._names[stage]

    @staticmethod
    def get_symbol(ability_class):
        
        if ability_class is not None:
            ability_class = ability_class.strip()

        if ability_class == "None":            
            symbol_str = "NONE!"
            raise Exception("X") 
        elif ability_class == AbilityClass.AMBUSH:
            ability_cls = "<ambush/>"
        elif ability_class == AbilityClass.SURPRISE:
            symbol_str = "<surprise/>"
        elif ability_class == AbilityClass.INITIATIVE:
            symbol_str = "<initiative/>"
        elif ability_class == AbilityClass.TALK:
            symbol_str = "<talk/>"
        elif ability_class == AbilityClass.START:
           symbol_str = "<start/>"
        elif ability_class == AbilityClass.FAST:
           symbol_str = "<fast/>"
        elif ability_class == AbilityClass.MEDIUM:
           symbol_str = "<medium/>"
        elif ability_class == AbilityClass.MEDIUM_OR_SLOW:
           symbol_str = "<mediumorslow/>"
        elif ability_class == AbilityClass.SLOW:
           symbol_str = "<slow/>"            
        elif ability_class == AbilityClass.FIGHT_REACH:
            symbol_str = "<fightreach/>"
        elif ability_class == AbilityClass.RESOLUTION:
            symbol_str = "<resolution/>"
        elif ability_class == AbilityClass.REACTION:
            symbol_str = "<reaction/>"
        elif ability_class == AbilityClass.START_AND_REACTION:
           symbol_str = "<startandreaction/>"            
        elif ability_class == AbilityClass.NON_COMBAT:
            symbol_str = "<noncombat/>"
        else:
            symbol_str = "UNKNOWN! %s" % ability_class
            raise Exception("X")
        return symbol_str

    
    @staticmethod
    def load(ability_class):
        ability_cls = AbilityClass.NONE

        if ability_class is not None:
            ability_class = ability_class.strip()

        if ability_class == "None":
            ability_cls = AbilityClass.NONE
        elif ability_class == "Surprise":
            ability_cls = AbilityClass.SURPRISE
        elif ability_class == "Initiative":
            ability_cls = AbilityClass.INITIATIVE
        elif ability_class == "Fight-Reach":
            ability_cls = AbilityClass.FIGHT_REACH
        elif ability_class == "resolution":
            ability_cls = AbilityClass.RESOLUTION
        elif ability_class == "Reaction":
            ability_cls = AbilityClass.REACTION
        elif ability_class == "Start":
            ability_cls = AbilityClass.START
        elif ability_class == "Fast":
            ability_cls = AbilityClass.FAST
        elif ability_class == "Medium":
            ability_cls = AbilityClass.MEDIUM
        elif ability_class == "Slow":
            ability_cls = AbilityClass.SLOW
        elif ability_class == "MediumOrSlow":
            ability_cls = AbilityClass.MEDIUM_OR_SLOW
        elif ability_class == "StartAndReaction":
            ability_cls = AbilityClass.START_AND_REACTION
        elif ability_class == "Non-Combat":
            ability_cls = AbilityClass.NON_COMBAT
        else:
            #raise Exception("Unknown ability class: %s" % ability_class)
            ability_cls = AbilityClass.NONE
        return ability_cls



class Ability:
    """
    An ability.

    """
    # set of all ability ids we've seen
    # there should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.title = None
        self.ability_id = None
        self.description = None
        self.tags = []
        self.ability_class = AbilityClass.NONE

        # A list of primary attibutes (Strength, Endurance etc whose modifiers
        # can be used when making this test).
        self.attr_modifiers = []

        # Is the ability a special racial/class ability?
        #
        # This differs from the concept of innateness in that an ability
        # can be innate to one archetype X and a second archetype Y can
        # learn that ability.
        #
        # Inborn abilities cannot be acquired during the game (except through
        # exceptional magical effects), e.g. if you're a dwarf you stay a dwarf
        # if you're not a dwarf you can't become one.  Abilties that apply
        # to dwarves alone.. always apply to dwarves alone.
        #
        self.inborn = None

        # mapping from
        self.levels = []        
        return

    def get_attr_modifiers(self):
        return self.attr_modifiers
    
    def get_ability_class_symbol(self):
        return AbilityClass.get_symbol(self.ability_class)
    
    def get_ability_class(self):
        return self.ability_class

    def get_description(self):
        return self.description

    def get_levels(self):
        return self.levels

    def get_title(self):
        return self.title

    def check_sanity(self):
        """
        Check to make sure that the ability is valid.

        """
        last_level_number = None
        is_first_level = True
        for ability_level in self.levels:
            level_number = ability_level.get_level_number()

            # check the first level is always 0 or 1
            if is_first_level:
                if level_number not in (0, 1):
                    raise Exception("First level for ability %s is %s should be 0 or 1"
                                    % (self.get_title(), level_number))
                is_first_level = False
            else:
                if last_level_number + 1 != level_number:
                    raise Exception("Bad level numbers for ability %s around level  %s"
                                    % (self.get_title(), level_number))            
            last_level_number = level_number
        return

    def get_id(self):
        return self.ability_id

    def get_ability_class(self):
        if self.ability_class is None:
            raise Exception("Missing ability class!")
        return self.ability_class

    def has_prerequisites(self):
        has_prereqs = False
        for level in self.levels:
            if level.has_prerequisites():
                has_prereqs = True
                break
        return has_prereqs


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
    

    def _parse_attr_modifiers(self, attr_modifiers_node):
        """An primary attribute whose modifiers can be used with this skill."""    
        for child in list(attr_modifiers_node):
           tag = child.tag

           if tag == "attr":
               attr = child.text.strip()
               if attr not in valid_attrs:
                   raise Exception("Received invalid attr. (%s) expecting "
                                   "one of %s\n" %
                                   (child.tag, ", ".join(valid_attrs)))
               self.attr_modifiers.append(attr)
                                      
           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag,
                                                      level.ability.fname))
        return

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


           elif tag == "inborn":
               if self.inborn is not None:
                   raise Exception("Only one inborn element per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.inborn = convert_str_to_bool(child.text)

           elif tag == "tag":
               self.tags.append(child.text)

           elif tag == "abilityclass":
               if child.text == "fast":
                   raise Exception("XXX")
               self.ability_class = AbilityClass.load(child.text)
               if self.ability_class == AbilityClass.NONE:
                   raise Exception("Unknown ability class: (%s) %s in %s\n" %
                                   (child.tag, child.text, self.fname))

           elif tag == "abilitylevels":
               if len(self.levels) > 0: #  is not None:
                   raise Exception("Only one abilitylevels per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.load_ability_levels(child)

           elif tag == "abilitydescription":
               if self.description is not None:
                   raise Exception("Only one abilitydescription per ability. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   #self.description = get_text(child)                   
                   #self.description = node_to_string(child)                   
                   self.description = children_to_string(child)                   

           elif tag == "abilityattrmodifiers":
               self._parse_attr_modifiers(child)
               
           # elif tag == "prerequisiteability":
           #     self.prerequisites.append(child.text)

           # elif tag == "prerequisitetag":
           #     prerequisite_tag = child.text
           #     if prerequisite_tag is not None:
           #         self.prerequisite_tags.append(prerequisite_tag)               

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN (%s) in file %s\n" % 
                               (child.tag, self.fname))

        # by default abilities are not inborn
        if self.inborn is None:
            self.inborn = False
        return


    def is_inborn(self):
        return self.inborn
    
    def load_ability_levels(self, ability_levels):
        # handle all the children
        for child in list(ability_levels):
        
           tag = child.tag
           if tag == "abilitylevel":

               level = AbilityLevel.load_ability_level(
                   fname = self.fname,
                   ability = self, 
                   ability_level_element = child)

               # check we don't already have an ability level with the same level number!
               for other_level in self.levels:
                   if other_level.get_level_number() == level.get_level_number():
                       raise Exception(
                           "Received two ability level definitions for ability: %s"
                           % level.get_title())
               self.levels.append(level)

           elif tag is COMMENT:
               # ignore comments!
               pass
           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

        # now sort the levels.
        def get_level_key(level):
            return level.level_number
        self.levels.sort(key = get_level_key)
        return


class AbilityGroupId:

    def __init__(self, ag_id, fname, line_number):
        self.ag_id = ag_id
        self.fname = fname
        self.line_number = line_number
        return 
    
    def __str__(self):
        return self.ag_id

    def __cmp__(self, other):
        return cmp(self.ag_id, other.ag_id)
        
    def get_location(self):
        return "%s:%s" % (self.fname, self.sourceline)


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


    def _load(self, ability_group_info_element):
        
        # handle all the children
        for child in list(ability_group_info_element):
        
           tag = child.tag
           if tag == "abilitygrouptitle":
               if self.title is not None:
                   raise Exception("Only one abilitygrouptitle per file.")
               else:
                   self.title = child.text.strip() 

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
                self.family = child.text
                assert self.family in ("Mundane", "Combat", "Magic")
                

           elif tag == "abilitygroupdescription":
               if self.description is not None:
                   raise Exception("Only one abilitygroupdescription per file.")
               else:
                   self.description = children_to_string(child)

           elif tag is COMMENT:
               pass # ignore comments!

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return



class AbilityGroup:
    xsd_schema = None

    def __init__(self, fname):
        self.fname = fname
        self.doc = parse_xml(fname)
        self.info = None
        self.abilities = []
        return

    def get_title(self):
        return self.info.title

    def get_abilities(self):
        return self.abilities
        
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

    def __cmp__(self, other):
        return cmp(self.get_title(), other.get_title())

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


class AbilityGroups:
    """
    A list of all abilities.

    """
    def __init__(self):
        self.ability_groups = []
        self.ability_lookup = {}
        return

    def __iter__(self):
        return iter(self.ability_groups)

    def get_ability_level(self, ability_level_id):
        return ability_level_lookup[ability_level_id]

    def get_abilities(self):
        for group in self.ability_groups:
            for ability in group.get_abilities():
                yield ability
        return
    
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
                
        # inform each ability about abilities that require it as a prerequisite
        for ability_group in self.ability_groups:
            for ability in ability_group.get_abilities():

                for ability_level in ability.get_levels():

                    for prereq in ability_level.get_ability_level_prereqs():
                        # for prereq_ability_level_id in ability_level.get_prerequisite_ids():

                        #if prereq_ability_level_id is None:
                        #    continue

                        # reqister this ability level with any prerequisites it might have
                        prereq_ability_level = AbilityLevel.get_level(prereq.ability_level_id)

                        if prereq_ability_level is None:
                            raise Exception(
                                ("No ability level matches prereq key: %s "
                                 "for ability: %s in file: %s") % 
                                (prereq.ability_level_id,
                                 ability_level.get_title(),
                                 ability.fname))
                        prereq_ability_level.add_dependency(ability_level.get_id())

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
    
    def get_ability_level_by_id(self, ability_level_id):
        return ability_level_lookup[ability_level_id]

    def get_ability_groups(self):
        return self.ability_groups
    
    def __getitem__(self, key):
        return self.ability_groups[key]

    
if __name__ == "__main__":

    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast = True)
    
    build_dir = join(root_dir, "build")
    #ability_groups.draw_all_skill_trees(build_dir)
    #ability_groups.draw_skill_tree(build_dir)
    #ability_groups.draw_skill_tree2(build_dir)

    count = 0
    
    for ability_group in ability_groups:
        #print(ability_group.get_title())

        #if "chool" not in ability_group.get_title():
        #    continue
        
        for ability in ability_group:
            count += 1
            print("\t%i %s" % (count, ability.get_title()))
            # # print("\t\t\tAbility Class: %s" % ability.get_ability_class())
            # # print("\t\t\tAbility Desc: %s" % ability.description)
            # # #print("\t\t\tAbility Class: %s" % ability.get_ability_class())
            # # #print("\t\t\t\t: %s" % ability.get_ability_class())
            
            # for ability_level in ability.get_levels():
            #     print("\t\t\t\t title %s" % ability_level.get_title())
            #     print("\t\t\t\t id %s" % ability_level.get_id())
            # #     print("\t\t\t\t2 %s" % ability_level.check)
            # #     print("\t\t\t\t3 %s" % ability_level.description)
            # # #    #print("\t\t\tLore: %s" % ability_level.get_default_lore())



