#!/usr/bin/env python
"""

 An Archetype is a class+race, e.g. Dwarven Shield Warrior.
 The code in here is used to parse the  


"""
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
from os import listdir
from utils import (
    parse_xml,
    validate_xml,
    node_to_string,
    COMMENT,
    convert_str_to_int,
    normalize_ws,
    parse_measurement_to_str,
    children_to_string,
    contents_to_string)    
from abilities import AbilityLevel


class NonUniqueTagError(Exception):
    """Expecting at most one of this sort of tag."""

    def __init__(self, tag, fname, line_number):
        super(NonUniqueTagError, self).__init__(
            "Only one tag: %s per file. %s:%s" % (tag, fname, line_number))
        return


class ModifiedAbilityLevel:
    """
    Modified ability/level for an archetype.

    """
    def __init__(self, group, modified_ability, ability_level):
        self.modified_ability_group = group
        self.modified_ability = modified_ability   
        self.ability_level = ability_level

        # has we been flagged as innate
        # (note that innateness is complicated to calculate and depends on
        # many things which might not be setr correctly.. this flag indicates
        # we the ability level *should* be innate)
        self.innate_flag = False

        # abilities can be enabled or disabled
        self.enabled = True
        return
    
    def get_ability(self):
        return self.modified_ability
    
    def get_effect(self):
        return self.ability_level.get_effect()
    
    def get_ability_class(self):
        return self.modified_ability.get_ability_class()
    
    def get_damage(self):
        return self.ability_level.get_damage()
    
    def get_check(self):
        return self.ability_level.get_check()
    
    def get_title(self):
        return self.ability_level.get_title()

    def get_overcharge(self):
        return self.ability_level.get_overcharge()

    def get_level_number(self):
        return self.ability_level.get_level_number()

    def is_enabled(self):
        return self.enabled

    def set_innate(self):              
        self.innate_flag = True

        # if an ability level is innate for a character then so are its
        # previous levels.
        lvl_num = self.ability_level.get_level_number()
        if lvl_num > 0:
            previous_lvl = self.modified_ability.get_modified_ability_level(lvl_num - 1)
            if previous_lvl is not None:
                previous_lvl.set_innate()
        return
    
    def get_mastery_successes(self):
        mastery_successes = self.ability_level.get_mastery_successes()
        return max(mastery_successes, 0)

    def get_mastery_attempts(self):
        mastery_attempts = self.ability_level.get_mastery_attempts()
        return max(mastery_attempts, 0)

    def get_mastery_failures(self):
        mastery_failures = self.ability_level.get_mastery_failures()
        return max(mastery_failures, 0)
    
    def is_innate(self, d = False):
        """
        You automatically get abilities with a zero cost and satisfied prereqs.
        Note.  

        """

        if self.innate_flag:
            return True
        return self.ability_level.is_innate()
    
    def is_innate_for_this_archetype(self):
        """Returns true if this ability level is innate for the archetype"""
        return (self.get_level_number() > 0 and
                self.is_innate() and
                "monster" not in self.ability_level.get_id()) # FIXME: HACK


class ModifiedAbility:
    """
    Modifiers to an ability for a archetype before we have the actual ability information.

    """
    def __init__(self, archetype, modified_ability_group, ability):
        self.archetype = archetype
        self.modified_ability_group = modified_ability_group
        # assert ability.__class__.__name__ == "Ability"

        self.ability = ability
        self.modified_ability_levels = []
        self.modified_ability_level_lookup = {}
        for ability_level in ability.get_levels():
            mal = ModifiedAbilityLevel(self.modified_ability_group,
                                       self, 
                                       ability_level)
            self.modified_ability_levels.append(mal)
            self.modified_ability_level_lookup[mal.get_level_number()] = mal
        return

    def get_ability_class(self):
        return self.ability.get_ability_class()

    def get_highest_innate_level(self):
        """
        Returns the highest innate ability level for the archetype or None.

        """
        innate_ability_level = None
        for ability_level in self.modified_ability_levels:
            if ability_level.is_innate():
                innate_ability_level = ability_level
            else:
                break
        return innate_ability_level

    def get_modified_ability_level(self, level):
        """Return a modified ability level or None."""
        return self.modified_ability_level_lookup.get(level)

    def get_title(self):
        return self.ability.get_title()

    def get_attr_modifiers(self):
       return self.ability.get_attr_modifiers()
    
    def get_attr_modifiers_str(self):
        return self.ability.get_attr_modifiers_str()

    def is_enabled(self):
        return self.enabled



class ModifiedAbilityGroup:
    """
    Modifiers for an ability group.

    """
    def __init__(self, archetype, ability_group):
        self.archetype = archetype
        self.ability_group = ability_group
        self.abilities = []

    def __iter__(self):
        return iter(self.abilities)

    def add_modified_ability(self, ability):
        assert ability.__class__.__name__ == "Ability"

        modified_ability = ModifiedAbility(archetype = self.archetype,
                                           modified_ability_group = self,
                                           ability = ability)
        self.abilities.append(modified_ability)
        return modified_ability
    
    def get_title(self):
        return self.ability_group.get_title()


class LevelProgressionData:
    """
    Information about going up a level for an Archetype.

    """

    def __init__(self, fname):

        # filename where this information is defined.
        self.fname = fname

        # this level number
        self.level_number = None

        # description
        self.level_description = None

        # hit points
        self.level_stamina = None
        self.level_stamina_refresh = None
        self.level_health = None
        self.level_health_refresh = None

        # level up ability gains and promotions
        self.level_abilities = []
        self.level_promotions = []

        # resolve pool
        self.level_resolve = None
        self.level_resolve_refresh = None
        
        # luck pool
        self.level_fate = None
        self.level_fate_refresh = None
        
        # magic pool
        self.level_magic_pool = None        
        self.level_magic_refresh = None        
        return

    def get_level_number(self):
        return self.level_number

    def get_new_ability_str(self):
        return ", ".join([str(ability) for ability in self.level_abilities])

    def get_new_ability_promotion_str(self):
        return ", ".join([str(promotion) for promotion in self.level_promotions])

    def load_or_level_abilities(self, or_node):
        abilities = []
        for child in list(or_node):
           tag = child.tag

           if tag is COMMENT:
               # ignore comments!
               pass
           else:
               abilities.append(tag)
        return abilities

    def load_level_abilities(self, node):
        for child in list(node):
           tag = child.tag
           if tag == "or":
               or_abilities = self.load_or_level_abilities(child)
               self.level_abilities.append(or_abilities)
           elif tag is COMMENT:
               # ignore comments!
               pass               
           else:
               self.level_abilities.append(tag)
           return
    
    def load_or_level_promotions(self, or_node):
        promotions = []
        for child in list(or_node):
           tag = child.tag
           if tag is COMMENT:
               # ignore comments!
               pass
           else:
               promotions.append(tag)
        return promotions

    def load_level_promotions(self, node):
        for child in list(node):
           tag = child.tag
           if tag == "or":
               or_promotions = self.load_or_level_abilities(child)
               self.level_promotions.append(or_promotions)
           elif tag is COMMENT:
               # ignore comments!
               pass               
           else:
               self.level_promotions.append(tag)
           return

    def load(self, archetype_node, fail_fast):
        # handle all the children
        for child in list(archetype_node):
        
           tag = child.tag
           if tag == "levelnumber":
               if self.level_number is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_number = int(child.text.strip())

           elif tag == "levelresolve":
               if self.level_resolve is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_resolve = contents_to_string(child)                   

           elif tag == "levelresolverefresh":
               if self.level_resolve_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_resolve_refresh = contents_to_string(child)

           elif tag == "levelstamina":
               if self.level_stamina is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_stamina = normalize_ws(child.text.strip())

           elif tag == "levelstaminarefresh":
               if self.level_stamina_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_stamina_refresh = normalize_ws(child.text.strip())

           elif tag == "levelhealth":
               if self.level_health is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                self.level_health = normalize_ws(child.text.strip())

           elif tag == "levelhealthrefresh":
               if self.level_health_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                self.level_health_refresh = normalize_ws(child.text.strip())

           elif tag == "levellore":
               if self.level_lore is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_lore = convert_str_to_int(child.text.strip())

           elif tag == "levelmartial":
               if self.level_martial is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_martial = convert_str_to_int(child.text.strip())

           elif tag == "levelgeneral":
               if self.level_general is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_general = convert_str_to_int(child.text.strip())

           elif tag == "levelmagical":
               if self.level_magical is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_magical = convert_str_to_int(child.text.strip())

           elif tag == "leveldescription":
               if self.level_description is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.level_description = contents_to_string(child)

           elif tag == "newlevelabilities":
               if len(self.level_abilities) > 0:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_abilities(child)

           elif tag == "newlevelpromotions":
               if len(self.level_promotions) > 0:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_promotions(child)

           elif tag == "levelmagicpool":
               if self.level_magic_pool is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_magic_pool = contents_to_string(child)
                       
           elif tag == "levelmagicrefresh":
               if self.level_magic_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_magic_refresh = contents_to_string(child)

           elif tag == "levelfate":
               if self.level_fate is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_fate = contents_to_string(child)

           elif tag == "levelfaterefresh":
               if self.level_fate_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_fate_refresh = contents_to_string(child)
                       
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        return
            


class LevelProgressionTable:
    """
    A list of level progression data for the Archetype, one for each level.

    """
    def __init__(self, fname):
        self.level_progression_data_list = []
        self.fname = fname
        return

    def load(self, level_progression_table_node, fail_fast):        

        # handle all the children
        for child in list(level_progression_table_node):
        
           tag = child.tag
           if tag == "level":
               level_progression_data = LevelProgressionData(self.fname)
               level_progression_data.load(child, fail_fast)
               self.level_progression_data_list.append(level_progression_data)

           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))

        self.level_progression_data_list.sort(key = lambda lpd: lpd.level_number)
        return

    def __iter__(self):
        return iter(self.level_progression_data_list)

    def __getitem__(self, index):
        return self.level_progression_data_list[index]



class Tags:
    """
    A list of archetype tags.

    """
    def __init__(self, fname):
        self.tags = []
        self.fname = fname
        return

    def load(self, archetype_tags_node, fail_fast):        
        # handle all the children
        for child in list(archetype_tags_node):
           tag = child.tag
           if tag == "tag":
               tag = child.text.strip().lower()
               self.tags.append(tag)
           elif tag is COMMENT:
               # ignore comments!
               pass
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        self.tags.sort()
        return

    def __iter__(self):
        return iter(self.tags)

    def __str__(self):
        return ", ".join(self.tags)

    def __contains__(self, key):
        return key.tag.lower() in self.tags


class AttrBonus(object):
    """
    Modifier to attributes based on archetype.

    """

    def __init__(self):
        self.attribute = None
        self.bonus = 0
        return

    def parse(self, fname, bonus_element):
        for child in list(bonus_element):
           tag = child.tag
           if tag == "attr":
               self.attribute = contents_to_string(child)

           elif tag == "value":
               try:
                   self.bonus = convert_str_to_int(contents_to_string(child))
               except ValueError as err:
                   ValueError("%s (%s) File: %s Line: %s\n" % 
                             (str(err), child.tag, fname, child.sourceline))
               
           elif tag is COMMENT:
               # ignore comments!
               pass
        
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return

    def __setattr__(self, attr, value):
        if attr == "bonus" and not isinstance(value, int):            
            raise Exception("Readonly")
	object.__setattr__(self, attr, value)
        return

    
    def __str__(self):
        return "{attribute:s} {bonus:+d}".format(**vars(self))


class AttrLimitType:
    MAX = "Max"
    MIN = "Min"
    

class AttrLimit:
    """
    Limit to attributes based on archetype.

    """

    def __init__(self):
        self.limit_type = None
        self.attribute = None
        self.limit = 0
        return

    def parse(self, fname, limit_type, limit_element):
        self.limit_type = limit_type
        
        for child in list(limit_element):
           tag = child.tag

           if tag == "attr":
               self.attribute = contents_to_string(child)

           elif tag == "value":
               try:
                   self.limit = convert_str_to_int(contents_to_string(child))
               except ValueError as err:
                   ValueError("%s (%s) File: %s Line: %s\n" % 
                             (str(err), child.tag, fname, child.sourceline))                   

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return
        
    def __str__(self):
        return "{limit_type} {attribute:s}: {limit:d}".format(**vars(self))

        
    


class Archetype:
    """
    Represents an Archetype.
    
    """
    def __init__(self, ability_groups, fname):
        self.fname = fname # save for debugging?
        self.title = None
        self.archetype_id = None
        self.ancestor_ids = [None, ]
        self.description = None
        self.ac = None
        self.move = None
        self.initiative = None
        self.aspect_examples = None
        self.starting_cash = None
        self.starting_gear = None
        self.initial_abilities = None

        self.height = None
        self.weight = None
        self.appearance = None
        self.age = None

        self.attr_bonuses = []
        self.attr_limits = []

        self.tags = Tags(fname)

        # each archetype has a local copy of the ability-group tree with local modifications.
        self.modified_abilities_lookup = {}
        self.modified_ability_groups_lookup = {}
        self.modified_ability_groups = []
        for ability_group in ability_groups:
            modified_ability_group = ModifiedAbilityGroup(self, ability_group)
            self.modified_ability_groups.append(modified_ability_group)
            self.modified_ability_groups_lookup[ability_group.get_id()] = modified_ability_group

            #print modified_ability_group
            for ability in ability_group.get_abilities():
                modified_ability = modified_ability_group.add_modified_ability(ability)
                self.modified_abilities_lookup[ability.get_id()] = modified_ability
        
        # Sort by group name
        self.modified_ability_groups.sort()

        #
        # FIXME: we need proper modified_ability_groups ..
        # just has innateness!!
        #        
        # self.modified_ability_groups = ability_groups

        # update these after a load
        self.innate_ability_levels = []
                
        # what advantages you get at what levels.
        self.level_progression_table = LevelProgressionTable(self.fname)        
        return

    def get_progression_data_for_level(self, level):
        return self.level_progression_table.level_progression_data_list[level]
    

    def get_attribute_limits_str(self):
        if len(self.attr_limits) == 0:
            attr_limits_str = "None"
        else:
            attr_limits_str = ", ".join([str(limit) for limit in self.attr_limits])
        return attr_limits_str

    def get_attribute_bonus_str(self):
        if len(self.attr_bonuses) == 0:
            attr_bonus_str = "None"
        else:
            attr_bonus_str = ", ".join([str(bonus) for bonus in self.attr_bonuses])
        return attr_bonus_str
    

    def get_modified_abilities(self):
        # abilities = self.modified_abilities_lookup.values()

        # def sort_fn(a, b):
        #     return cmp(a.get_title(), b.get_title())
        
        # abilities.sort(sort_fn)
        # return abilities
        return []
        
    
    def has_magical_abilities(self):
        has_magical_abilities = False
        for modified_ability_group in self.modified_ability_groups:
            if modified_ability_group.get_family() == "Magic":
                for modified_ability in modified_ability_group:
                    if modified_ability.is_enabled():
                        has_magical_abilities = True
                        break
        return has_magical_abilities
    

    def get_archetype_specific_innate_ability_levels(self):
        """
        Returns the innate ability levels specific to this archetype.

        """
        return [ ability_level for ability_level in self.innate_ability_levels if 
                 ability_level.is_innate_for_this_archetype() ]
 
    def get_armour_class(self):
        return self.ac

    def get_move(self):
        return self.move

    def get_initiative_bonus(self):
        return self.initiative

    def get_modified_ability(self, ability_id):
        #return self.modified_abilities_lookup[ability_id]
        return []

    def get_groups(self):
        return self.modified_ability_groups

    def get_filtered_groups(self):
        """
        Return a list of groups with abilities the archetype can actually take.

        """
        # return [
        #     group for group in self.modified_ability_groups
        #     if len(group.get_filtered_abilities()) > 0 ]
        return [
            group for group in self.modified_ability_groups   ## FIXME: filter disabled?
            if len(group.get_filtered_abilities()) > 0 ]

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description
        
    def get_initial_abilities(self):
        return self.initial_abilities
        
    def has_tags(self):
        return len(self.tags) > 0

    def get_tags_str(self):
        return ", ".join(self.tags)

    def get_starting_gear(self):
        return self.starting_gear

    def get_starting_cash(self):
        return self.starting_cash

    def get_initiative(self):
        return self.initiative
    
    def get_level_progression_table(self):
        return self.level_progression_table

    def get_id(self):
        return self.archetype_id

    def load(self, archetype_node, fail_fast):
        try:
            self._load(archetype_node, fail_fast)

            # sort the ability levels
            self.innate_ability_levels.sort(key = lambda mal: mal.get_title())

            # update the innate abilities
            # for ability in list(self.modified_abilities_lookup.values()):
            #     levels = ability.get_levels()
            #     max_level = None
            #     for level in levels:
            #         if not level.is_innate():
            #             continue

            #         if (max_level is None or 
            #             (max_level.get_level_number() < level.get_level_number())):
            #             max_level = level

            #     if max_level is not None:
            #         self.innate_ability_levels.append(max_level)

            # update the enabled flag in all the ability groups, abilities and levels
            # (it might be out of date here)
            # for ability_group in self.modified_ability_groups:

            #     # if a group is disabled all it's levels and abilities are also disabled.
            #     if not ability_group.is_enabled():
            #         for ability in ability_group.get_abilities():                    
            #             ability.set_enabled(False)

            #     else:
            #         # otherwise an ability group is disabled if all it's abilities are.
            #         all_abilities_disabled = True
            #         for ability in ability_group.get_abilities():
            #             if ability.is_enabled():
            #                 all_abilities_disabled = False
            #                 break

            #         if all_abilities_disabled:
            #             ability_group.set_enabled(False)

            #         else:

            #             # now disable abilities on a per ability basis
            #             for ability in ability_group.get_abilities():
            #                 if not ability.is_enabled():
            #                     ability.set_enabled(False)

            #             # also an ability is disabled if all its levels are.
            #             all_ability_levels_disabled = True
            #             for ability_level in ability:
            #                 if ability_level.is_enabled():
            #                     all_ability_levels_disabled = False
            #                     break

            #                 if all_ability_levels_disabled:
            #                     ability.set_enabled(False)
        except:
            print "Problem trying to parse archetype file: %s" % self.fname
            raise

        # after we've loaded all the archertype ability information
        # go through and set the innate information for prerequisites
        #self.set_innate_abilities() ###########################################
        # for ability in self.modified_abilities_lookup.values():
        #     for ability_level in ability:
        #         ability_level.check_consistency()

        self.check_consistency()                
        return True
    

    def check_consistency(self):        
        if self.initial_abilities is None:
            raise Exception("Missing 'initial_abilities' in file: %s" % self.fname)
        return


    def _load(self, archetype_node, fail_fast):
        # handle all the children
        for child in list(archetype_node):
        
           tag = child.tag
           if tag == "archetypetitle":
               if self.title is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.title = child.text.strip() 

           elif tag == "archetypeid":
               if self.archetype_id is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.archetype_id = child.text.strip() 

           elif tag == "archetypeac":
               if self.ac is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.ac = child.text.strip()

           elif tag == "archetypemove":
               if self.move is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.move = child.text.strip() 

           elif tag == "inheritance":
               self._load_inheritance(inheritance = child)

           elif tag == "archetypedescription":
               if self.description is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.description = children_to_string(child)

           elif tag == "archetypeinitiative":
               if self.initiative is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
                   #raise Exception("Only one archetypeinitiative per file.")
               else:
                   self.initiative = convert_str_to_int(child.text)

           elif tag == "startingcash":
               if self.starting_cash is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.starting_cash = child.text

           elif tag == "startinggear":
               if self.starting_gear is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.starting_gear = normalize_ws(child.text)

           elif tag == "height":
               if self.height is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.height = parse_measurement_to_str(self.fname, child)

           elif tag == "weight":
               if self.weight is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.weight = parse_measurement_to_str(self.fname, child)

           elif tag == "appearance":
               if self.appearance is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.appearance = normalize_ws(child.text)

           elif tag == "age":
               if self.age is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.age = normalize_ws(child.text)

           elif tag == "aspectexamples":
               if self.aspect_examples is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.aspect_examples = child.text

           elif tag == "archetypetags":
               self.tags.load(child, fail_fast)

           elif tag == "archetypeinitialabilities":
               if self.initial_abilities is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.initial_abilities = children_to_string(child)

           elif tag == "levelprogressiontable":
               self.level_progression_table.load(child, fail_fast)

           elif tag == "abilitymodifiers":
               self._load_ability_modifiers(child)

           elif tag == "attrbonus":
               bonus = AttrBonus()
               bonus.parse(self.fname, child)
               self.attr_bonuses.append(bonus)

           elif tag == "attrmax":
               attr_max = AttrLimit()
               attr_max.parse(self.fname, AttrLimitType.MAX, child)
               self.attr_limits.append(attr_max)

           elif tag == "attrmin":
               attr_min = AttrLimit()
               attr_min.parse(self.fname, AttrLimitType.MIN, child)
               self.attr_limits.append(attr_min)

           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        return
            

    def _load_inheritance(self, inheritance):
        """
        Parse the <inheritance> element and its children.

        """
        # handle all the children
        for child in list(inheritance):
           tag = child.tag

           if tag == "ancestor":
               ancestor_id = child.text.strip()
               self.ancestors.append(ancestor_id)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        return


    def _load_innate_ability_modifier(self, innate_node):
        ability_id = None
        ability_level = None
        
        # handle all the children
        for child in list(innate_node):
           tag = child.tag

           if tag == "abilityid":
               if ability_id is not None:
                   raise Exception("Only one id per ability modifier!")
               else:
                   ability_id = child.text.strip()    

           elif tag == "level":
               ability_level = convert_str_to_int(child.text)

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))

        if ability_id not in self.modified_abilities_lookup:
            raise Exception("Unknown ability id: '%s' in archetype file: %s Line: %s\n" % 
                            (ability_id, self.fname, child.sourceline))
        else:        
            ability = self.modified_abilities_lookup[ability_id]
        
        ability_level = ability.get_modified_ability_level(ability_level)
        ability_level.set_innate()
        return


    def _load_ability_modifiers(self, ability_modifiers):
        """
        Load a bunch of ability modifiers.

        """
        # handle all the children
        for child in list(ability_modifiers):
           tag = child.tag

           if tag == "abilitymodifier":
               self._load_ability_modifier(child)

           elif tag == "abilitygroupmodifier":
               self._load_ability_group_modifier(child)

           elif tag == "disable":
               #self.set_enabled(child, False)
               pass

           elif tag == "enable":
               #self.set_enabled(child, True)
               pass

           elif tag == "innate":
               self._load_innate_ability_modifier(child)

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        return
           

    def _load_ability_modifier(self, ability_modifier):
        ability_id = None
        lore_point_modifier = 0
        martial_point_modifier = 0
        general_point_modifier = 0
        magical_point_modifier = 0
        successes_modifier = 0
        attempts_modifier = 0
        failures_modifier = 0
        
        # parse ability level modifiers last.
        ability_level_modifier_elements = []

        # handle all the children
        for child in list(ability_modifier):
           tag = child.tag

           if tag == "abilityid":
               if ability_id is not None:
                   raise Exception("Only one id per ability modifier!")
               else:
                   ability_id = child.text.strip()               

           elif tag == "lorepointmodifier":
               lore_point_modifier = convert_str_to_int(child.text)

               
           elif tag == "martialpointmodifier":
               martial_point_modifier = convert_str_to_int(child.text)
               
           elif tag == "generalpointmodifier":
               self.general_point_modifier = convert_str_to_int(child.text)

           elif tag == "magicalpointmodifier":
               self.magical_point_modifier = convert_str_to_int(child.text)

           elif tag == "abilitylevelmodifier":
               ability_level_modifier_elements.append(child)

           elif tag == "successesmodifier":
               successes_modifier = convert_str_to_int(child.text)

           elif tag == "failuresmodifier":
               failures_modifier = convert_str_to_int(child.text)

           elif tag == "attemptsmodifier":
               attempts_modifier = convert_str_to_int(child.text)

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
           
        # if ability_id not in self.modified_abilities_lookup:
        #     raise Exception("UNKNOWN ABILITY (%s) File: %s Line: %s\n" % 
        #                        (ability_id, self.fname, child.sourceline))

        # modified_ability = self.modified_abilities_lookup[ability_id]
        # modified_ability.martial_point_modifier = martial_point_modifier
        # modified_ability.lore_point_modifier = lore_point_modifier
        # modified_ability.general_point_modifier = general_point_modifier
        # modified_ability.magical_point_modifier = magical_point_modifier
        # modified_ability.successes_modifier = successes_modifier
        # modified_ability.failures_modifier = failures_modifier
        # modified_ability.attempts_modifier = attempts_modifier

        # # handle
        # for child in ability_level_modifier_elements:
        #     modified_ability.load_ability_level_modifier(child)
        
        return


    def _load_ability_group_modifier(self, ability_group_modifier):

        ability_group_id = None
        lore_point_modifier = 0
        martial_point_modifier = 0
        general_point_modifier = 0
        magical_point_modifier = 0
        successes_modifier = 0
        attempts_modifier = 0
        failures_modifier = 0
        
        # handle all the children
        for child in list(ability_group_modifier):
           tag = child.tag

           if tag == "abilitygroupid":
               if ability_group_id is not None:
                   raise Exception("Only one id per ability group modifier!")
               else:
                   ability_group_id = child.text.strip()

                   # if ability_group_id not in self.modified_ability_groups_lookup:
                   #     raise Exception("UNKNOWN ABILITY GROUP ID (%s) File: %s Line: %s\n" % 
                   #                     (ability_group_id, self.fname, child.sourceline))

           elif tag == "lorepointmodifier":
               lore_point_modifier = convert_str_to_int(child.text)
               
           elif tag == "martialpointmodifier":
               martial_point_modifier = convert_str_to_int(child.text)
               
           elif tag == "generalpointmodifier":
               general_point_modifier = convert_str_to_int(child.text)
               
           elif tag == "magicalpointmodifier":
               magical_point_modifier = convert_str_to_int(child.text)

           elif tag == "successesmodifier":
               successes_modifier = convert_str_to_int(child.text)

           elif tag == "failuresmodifier":
               failures_modifier = convert_str_to_int(child.text)

           elif tag == "attemptsmodifier":
               attempts_modifier = convert_str_to_int(child.text)

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))

        # modified_ability_group = self.modified_ability_groups_lookup[ability_group_id]
        # modified_ability_group.lore_point_modifier = lore_point_modifier
        # modified_ability_group.martial_point_modifier = martial_point_modifier
        # modified_ability_group.general_point_modifier = general_point_modifier
        # modified_ability_group.magical_point_modifier = magical_point_modifier
        # modified_ability_group.successes_modifier = successes_modifier
        # modified_ability_group.attempts_modifier = attempts_modifier
        # modified_ability_group.failures_modifier = failures_modifier

        ## assert self.ability_id is not None
        ## return ability_modifier
        return


class Archetypes:
    """
    A list of all enabled archetypes.

    """
    def __init__(self):
        self.archetypes = []
        self.archetype_lookup = {}
        return

    def __iter__(self):
        return iter(self.archetypes)

    def __getitem__(self, key):
         return self.archetype_lookup[key]

 
    def load_archetypes_from_xml(self, xml_fname, abilities, fail_fast):
        """
        Load all the archetypes in an xml file.

        """
        archetypes_in_file = []

        # parse the xml
        doc = parse_xml(xml_fname)

        if doc is None:
            raise Exception("Errors in %s" % xml_fname)

        # validate
        error_log = validate_xml(doc)
        if error_log is not None:
            print("Errors (XSD)!")
            print(error_log)
            raise Exception("Errors in %s" % xml_fname)

        root = doc.getroot()
        archetype_nodes = root.xpath("//archetype")

        for archetype_node in archetype_nodes:
            archetype = Archetype(abilities, xml_fname)
            archetype.load(archetype_node, fail_fast)
            archetypes_in_file.append(archetype)
        return archetypes_in_file

    
    def load(self, ability_groups, archetypes_dir, fail_fast):
        """
        Load all the archetypes in all the xml files in the docs_dir.
        Archetype files start with "archetype_" and end with ".xml"

        """
        for xml_fname in listdir(archetypes_dir):
            fname = basename(xml_fname)          

            if not xml_fname.endswith(".xml"):
                continue

            full_xml_fname = join(archetypes_dir, xml_fname)
            archetypes_in_file = self.load_archetypes_from_xml(
                full_xml_fname, ability_groups, fail_fast)

            for archetype in archetypes_in_file:
                key = archetype.get_id()
                if key in self.archetype_lookup:
                    raise Exception("The same archetype key: %s is used in two archetypes! "
                                    "See file: %s and file: %s" % (
                                        key,
                                        self.archetype_lookup[key].fname,
                                        xml_fname))
                self.archetype_lookup[key] = archetype
                self.archetypes.append(archetype)
        return


if __name__ == "__main__":

    src_dir = abspath(join(dirname(__file__)))
    root_dir = abspath(join(src_dir, ".."))
    #sys.path.append(src_dir)

    from abilities import AbilityGroups
    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast = True)

    archetypes = Archetypes()
    archetypes_dir = join(root_dir, "archetypes")
    archetypes.load(ability_groups, archetypes_dir, fail_fast = True)
    #build_dir = join(root_dir, "build")
    #archetypes.write_abilities_xml_to_dir(build_dir)

    for archetype in archetypes:

        #if "Outrider" not in archetype.get_title():
        #    continue
        
        print("Archetype: %s" % archetype.get_title())        
        print("initial abilities: %s\n" % archetype.get_initial_abilities())
        # for ability_group in archetype.modified_ability_groups:
        #     #if "onster" not in ability_group.get_title():
        #     #   continue            

        #     #print("\t%s" % ability_group.get_title())
        #     # for ability in ability_group:

        #     #     #if "Negotiate" not in ability.get_title():
        #     #     #    continue
                
        #     #     print("\t\t%s" % ability.get_title())
        #     #     print("\t\tHighest innate level %s" % ability.get_highest_innate_level())
                
        #     #     for mal in ability.get_levels():
        #     #         print("\t\t\t%s %s" % (mal.get_title(), mal.get_total_point_cost()))
        #     #         print("\t\t\tIS INNATE %s" % mal.is_innate(d = True))
        #     #         print("\t\t\t\tRecommended: %s" % mal.is_recommended())        
        #     #         print("\t\t\t\tArch Innate: %s" %
        #     #               mal.is_innate_for_this_archetype())
        #     #         print("\t\t\t\tEnabled?: %s" %
        #     #               mal.is_enabled())
