#!/usr/bin/env python
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

from abilities import AbilityGroup, AbilityGroups



# class NonUniqueTagError(Exception):
#     """Expecting at most one of this sort of tag."""

#     def __init__(self, tag, fname, line_number):
#         super(NonUniqueTagError, self).__init__(
#             "Only one tag: %s per file. %s:%s" % (tag, fname, line_number))
#         return

# class ModifiedAbilityLevel:
#     """
#     Modified ability/level for an patron.

#     """

#     def __init__(self, group, modified_ability, ability_level):
#         self.modified_ability_group = group
#         self.modified_ability = modified_ability   
#         self.ability_level = ability_level

#         # shorthand
#         self.patron = modified_ability.patron

#         # modifications to the point cost at the specific ability level
#         self.martial_point_modifier = 0
#         self.general_point_modifier = 0
#         self.lore_point_modifier = 0
#         self.magical_point_modifier = 0

#         # is this a recommended ability at first level?
#         self.recommended = False

#         # has we been flagged as innate
#         # (note that innateness is complicated to calculate and depends on
#         # many things which might not be setr correctly.. this flag indicates
#         # we the ability level *should* be innate)
#         self.innate_flag = False

#         # abilities can be enabled or disabled
#         # if an ability is enabled or disabled it overrides the group setting
#         self.enabled = True

#         # level mastery modifiers
#         self.successes_modifier = 0
#         self.failures_modifier = 0
#         self.attempts_modifier = 0
#         return

#     def get_effect(self):
#         return self.ability_level.get_effect()
    
#     def get_ability_class(self):
#         return self.modified_ability.get_ability_class()
    
#     def get_family(self):
#         return self.modified_ability_group.get_family()

#     def get_damage(self):
#         return self.ability_level.get_damage()
    
#     def get_check(self):
#         return self.ability_level.get_check()
    
#     def get_title(self):
#         return self.ability_level.get_title()

#     def get_overcharge(self):
#         return self.ability_level.get_overcharge()

#     def get_level_number(self):
#         return self.ability_level.get_level_number()

#     def set_enabled(self, enabled):
#         self.enabled = enabled
#         return

#     def is_enabled(self):
#         return self.enabled

#     def should_appear_in_patron_list(self):
#         """
#         An ability level should only appear in an patrons purchase list if it's
#         enabled and it's level is >= the lowest innate level.

#         """
#         should_appear = True
#         if not self.is_enabled():
#             should_appear = False
#         else:            
#             innate_level = self.modified_ability.get_highest_innate_level()
#             if innate_level is not None:
#                 should_appear = innate_level.get_level_number() <= self.get_level_number()
#         return should_appear

#     def get_martial_points(self):
#         if self.innate_flag or self.get_level_number() == 0:
#             return 0
#         martial_points = (self.ability_level.get_default_martial() +
#                           self.martial_point_modifier +
#                           self.modified_ability_group.get_martial_point_modifier())
#         return max(martial_points, 0)

#     def get_lore_points(self):
#         if self.innate_flag or self.get_level_number() == 0:
#             return 0

#         lore_points = (
#             self.ability_level.get_default_lore() +
#             self.lore_point_modifier +                    # level modifier
#             self.modified_ability.get_lore_point_modifier() +   # ability modifier
#             self.modified_ability_group.get_lore_point_modifier()) # group modifier
#         return max(lore_points, 0)

#     def get_general_points(self):
#         if self.innate_flag or self.get_level_number() == 0:
#             return 0

#         general_points = (
#             self.ability_level.get_default_general() +
#             self.general_point_modifier +
#             self.modified_ability.get_general_point_modifier() +   # ability modifier
#             self.modified_ability_group.get_general_point_modifier())
#         return max(general_points, 0)

#     def get_magical_points(self):

#         if self.innate_flag or self.get_level_number() == 0:
#             return 0

#         magical_points = (
#             self.ability_level.get_default_magical() +
#             self.magical_point_modifier +
#             self.modified_ability.get_magical_point_modifier() +   # ability modifier
#             self.modified_ability_group.get_magical_point_modifier())
#         return max(magical_points, 0)


#     def set_innate(self):              
#         print "Set %s innate " % self.get_title()

#         self.innate_flag = True
#         self.martial_point_modifier -= self.get_martial_points() 
#         self.general_point_modifier -= self.get_general_points() 
#         self.lore_point_modifier -= self.get_lore_points() 
#         self.magical_point_modifier -= self.get_magical_points()

#         print "martial %s " % self.get_martial_points() 
#         print "general %s " % self.get_general_points() 
#         print "lore %s" % self.get_lore_points() 
#         print "megical %s" % self.get_magical_points()

#         #if "Club" in self.get_title():
#         print "--------------------"
#         print "Set level innate %s" % self.ability_level.get_title()

#         # if an ability level is innate for a character then so are its
#         # previous levels.
#         lvl_num = self.ability_level.get_level_number()
#         if lvl_num > 0:
#             previous_lvl = self.modified_ability.get_modified_ability_level(lvl_num - 1)
#             if previous_lvl is not None:
#                 previous_lvl.set_innate()
#         return


#     def check_consistency(self):
#         """
#         Called after we've loaded all the abilities.

#         """
#         # Note: it's important that we actually check for the innate flag
#         # and not is_innate() here!
#         if self.innate_flag:

#             # check prerequisite tags
#             for prereq_tag in self.ability_level.get_prerequisite_tags():
#                 if prereq_tag not in self.patron.tags:
#                     raise Exception("For patron %s the ability %s is marked innate but "
#                                     "the patron lacks the required prerequisite tag: %s "
#                                     % (self.patron.get_title(),
#                                        self.get_title(),
#                                        str(prereq_tag)))                
#             #
#             # Innate abilities don't have to have innate parents!
#             # 
                
#             # # check ability level prerequisites
#             # for ability_level_prereq in self.ability_level.get_ability_level_prereqs():
            
#             #     # get the unmodified ability.
#             #     ability_level_id = ability_level_prereq.get_ability_level_id()
#             #     ability_level = AbilityLevel.get_level(ability_level_id)
#             #     ability = ability_level.ability
        
#             #     # get the ability level
#             #     level_num = ability_level.get_level_number()
            
#             #     # get the prereq modified ability level.
#             #     modified_ability = self.patron.get_modified_ability(ability.ability_id)
#             #     modified_ability_level = modified_ability.get_modified_ability_level(level_num)

#             #     assert modified_ability_level is not None
                
#             #     if not modified_ability_level.is_innate():
#             #         raise Exception("Patron %s has an ability level %s that is innate "
#             #                         "but it has a prerequisite %s that is not innate!" %
#             #                         (self.patron.get_title(), self.get_title(),
#             #                          modified_ability_level.get_title()))
#         return
    
#     def get_mastery_successes(self):
#         mastery_successes = (
#             self.ability_level.get_mastery_successes() + 
#             self.successes_modifier +
#             self.modified_ability.get_successes_modifier() +   # ability modifier
#             self.modified_ability_group.get_successes_modifier())
#         return max(mastery_successes, 0)

#     def get_mastery_attempts(self):
#         mastery_attempts = (
#             self.ability_level.get_mastery_attempts() + 
#             self.attempts_modifier +
#             self.modified_ability.get_attempts_modifier() +   # ability modifier
#             self.modified_ability_group.get_attempts_modifier())
#         return max(mastery_attempts, 0)

#     def get_mastery_failures(self):
#         mastery_failures = (
#             self.ability_level.get_mastery_failures() + 
#             self.failures_modifier +
#             self.modified_ability.get_failures_modifier() +   # ability modifier
#             self.modified_ability_group.get_failures_modifier())
#         return max(mastery_failures, 0)


#     def get_total_point_cost(self):
#         return (self.get_martial_points() +
#                 self.get_general_points() +
#                 self.get_lore_points() +
#                 self.get_magical_points())


#     def is_recommended(self):
#         return self.recommended
    
#     def is_innate(self, d = False):
#         """
#         You automatically get abilities with a zero cost and satisfied prereqs.
#         Note.  

#         """
#         if self.innate_flag:
#             return True
        
#         lvl_num = self.ability_level.get_level_number()

#         # if d:
#         #     print lvl_num

#         if lvl_num <= 1:
#             previous_level_is_innate = True
#         else:
#             previous_lvl = self.modified_ability.get_modified_ability_level(lvl_num - 1)
#             previous_level_is_innate = previous_lvl.is_innate()

#         # sanity check: level 0 abilities must have 0 cost
#         if lvl_num == 0:
#             if (self.get_martial_points() != 0 or
#                 self.get_general_points() != 0 or 
#                 self.get_lore_points() != 0 or 
#                 self.get_magical_points() != 0):
            
#                 costs = "%s/%s/%s/%s/%s" % (self.get_martial_points(),
#                                             self.get_general_points(),
#                                             self.get_lore_points(),
#                                             self.get_magical_points())
            
#                 raise Exception("Level 0 abilities must be innate! [%s:%s] has non zero points "
#                                 "for var in collection: patron %s, costs are: %s" % 
#                                 (self.modified_ability_group.get_title(), 
#                                  self.modified_ability.get_title(), 
#                                  self.patron.get_title(),
#                                  costs))                            

#         # check for prerequisite abilities.
#         all_prerequisites_are_innate = True 
#         for prereq in self.ability_level.get_ability_level_prereqs():
           
#             # this next bit is all fiddling with the unmodified abilities.
#             unmodified_prereq_lvl = AbilityLevel.get_level(prereq.ability_level_id)
#             unmodified_prereq_ability = unmodified_prereq_lvl.ability
#             unmodified_ability_id = unmodified_prereq_ability.get_id()
#             lvl_number = unmodified_prereq_lvl.get_level_number()

#             # now get the modified ability level
#             modified_prereq_ability = self.patron.get_modified_ability(unmodified_ability_id)
#             modified_prereq_lvl = modified_prereq_ability.get_modified_ability_level(lvl_number)
            
#             # and check it's innate
#             if not modified_prereq_lvl.is_innate():
#                 all_prerequisites_are_innate = False
#                 break

#         # check for prerequisite tags
#         has_prerequisite_tags = True
#         for prereq_tag in self.ability_level.get_prerequisite_tags():
#             if prereq_tag not in self.patron.tags:
#                 has_prerequisite_tags = False

#         # if d:
#         #     print self.get_title()
#         #     print "previous level is innate %s" % previous_level_is_innate
#         #     print "has prereqs %s " % has_prerequisite_tags
#         #     print "all_prerequisites_are_innate %s" % all_prerequisites_are_innate
#         #     print "point cost is zero %s " % (self.get_total_point_cost() == 0)
#         #     print "\tmartial %s " % self.get_martial_points()
#         #     print "\tgeneral %s " % self.get_general_points()
#         #     print "\tlore %s " % self.get_lore_points()
#         #     print "\tmagical %s " % self.get_magical_points()
                

#         return (previous_level_is_innate and
#                 has_prerequisite_tags and
#                 all_prerequisites_are_innate and 
#                 self.get_total_point_cost() == 0)
    
#     def is_innate_for_this_patron(self):
#         """Returns true if this ability level is innate for the patron"""
#         return self.get_level_number() > 0 and self.is_innate()

#     def get_prerequisites(self):
#         return self.ability_level.get_prerequisites()
    
#     def has_prerequisites(self):
#         return self.ability_level.has_prerequisites()

#     def __str__(self):
#         return str(self.ability_level)



# class ModifiedAbility:
#     """
#     Modifiers to an ability for a patron before we have the actual ability information.

#     """
#     def __init__(self, patron, modified_ability_group, ability):
#         self.patron = patron
#         self.modified_ability_group = modified_ability_group
#         assert ability.__class__.__name__ == "Ability"

#         self.ability = ability        
#         self.modified_ability_levels = []
#         self.modified_ability_level_lookup = {}
#         for ability_level in ability.get_levels():
#             mal = ModifiedAbilityLevel(self.modified_ability_group,
#                                        self, 
#                                        ability_level)
#             self.modified_ability_levels.append(mal)
#             self.modified_ability_level_lookup[mal.get_level_number()] = mal

#         self.martial_point_modifier = 0
#         self.general_point_modifier = 0
#         self.lore_point_modifier = 0
#         self.magical_point_modifier = 0

#         # ability mastery modifiers
#         self.successes_modifier = 0
#         self.failures_modifier = 0
#         self.attempts_modifier = 0

#         # abilities can be enabled or disabled
#         # if an ability is enabled or disabled it overrides the group setting
#         self.enabled = True
#         return

#     def get_ability_class(self):
#         return self.ability.get_ability_class()

#     def get_highest_innate_level(self):
#         """
#         Returns the highest innate ability level for the patron or None.

#         """
#         innate_ability_level = None
#         for ability_level in self.modified_ability_levels:
#             if ability_level.is_innate():
#                 innate_ability_level = ability_level
#             else:
#                 break
#         return innate_ability_level
    
    
#     def get_modified_ability_level(self, level):
#         """Return a modified ability level or None."""
#         return self.modified_ability_level_lookup.get(level)

#     def __iter__(self):
#         return iter(self.modified_ability_levels)

#     def get_title(self):
#         return self.ability.get_title()


#     def get_innate_ability_level(self):
#         """
#         Returns the highest innate ability level (the ability level that has a 
#         zero point cost) if this ability is not disabled for this patron.  
#         Disabled abilities are set in the patron.  Returns None otherwise..

#         """
#         if self.is_disabled() or self.modified_ability_group.is_disabled():
#             return None

#         innate_level = None
#         for level in self.levels:
#             if level.is_innate() and not level.is_disabled():
#                 innate_level = level
#             else:
#                 break

#         return innate_level


#     def get_levels(self):
#         return self.modified_ability_levels

#     def set_enabled(self, enabled):
#         self.enabled = enabled
#         for ability_level in self.modified_ability_levels:
#             ability_level.set_enabled(enabled)
#         return

#     def is_enabled(self):
#         return self.enabled

#     def get_martial_point_modifier(self):
#         return self.martial_point_modifier

#     def get_general_point_modifier(self):
#         return self.general_point_modifier
    
#     def get_lore_point_modifier(self):
#         return self.lore_point_modifier

#     def get_magical_point_modifier(self):
#         return self.magical_point_modifier

#     def get_successes_modifier(self):
#         return self.successes_modifier

#     def get_attempts_modifier(self):
#         return self.attempts_modifier

#     def get_failures_modifier(self):
#         return self.failures_modifier

#     def load_ability_level_modifier(self, ability_level_modifier):
#         ability_id = None
#         lore_point_modifier = 0
#         martial_point_modifier = 0
#         general_point_modifier = 0
#         magical_point_modifier = 0
#         successes_modifier = 0
#         attempts_modifier = 0
#         failures_modifier = 0
#         recommended = False
        
#         # handle all the children
#         for child in list(ability_level_modifier):
#            tag = child.tag

#            if tag == "level":
#                level_id = convert_str_to_int(child.text)

#            elif tag == "lorepointmodifier":
#                lore_point_modifier = convert_str_to_int(child.text)
               
#            elif tag == "martialpointmodifier":
#                martial_point_modifier = convert_str_to_int(child.text)
               
#            elif tag == "generalpointmodifier":
#                general_point_modifier = convert_str_to_int(child.text)

#            elif tag == "magicalpointmodifier":
#                magical_point_modifier = convert_str_to_int(child.text)

#            elif tag == "successesmodifier":
#                successes_modifier = convert_str_to_int(child.text)

#            elif tag == "failuresmodifier":
#                failures_modifier = convert_str_to_int(child.text)

#            elif tag == "attemptsmodifier":
#                attempts_modifier = convert_str_to_int(child.text)

#            elif tag == "recommended":
#                recommended = True

#            elif tag is COMMENT:
#                # ignore comments!
#                pass

#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, self.fname, child.sourceline))

#         modified_ability_level = self.modified_ability_level_lookup[level_id]
#         modified_ability_level.martial_point_modifier = martial_point_modifier
#         modified_ability_level.lore_point_modifier = lore_point_modifier
#         modified_ability_level.general_point_modifier = general_point_modifier
#         modified_ability_level.magical_point_modifier = magical_point_modifier
#         modified_ability_level.successes_modifier = successes_modifier
#         modified_ability_level.attempts_modifier = attempts_modifier
#         modified_ability_level.failures_modifier = failures_modifier
#         return



# class ModifiedAbilityGroup:
#     """
#     Modifiers for an ability group.

#     """
#     def __init__(self, patron, ability_group):
#         self.patron = patron
#         self.ability_group = ability_group
#         self.abilities = []

#         # by default abilities are enabled
#         # (you have to disable the groups or individual abilities to turn them off
#         # you can also disable a group and enable an ability in the group)
#         self.enabled = True

#         self.martial_point_modifier = 0        
#         self.general_point_modifier = 0        
#         self.lore_point_modifier = 0        
#         self.magical_point_modifier = 0        

#         # ability group mastery modifiers
#         self.successes_modifier = 0
#         self.failures_modifier = 0
#         self.attempts_modifier = 0
#         return

#     def get_family(self):
#         return self.ability_group.get_family()

#     def __iter__(self):
#         return iter(self.abilities)

#     def set_enabled(self, enabled):
#         self.enabled = enabled
#         for ability in self.abilities:
#             ability.set_enabled(enabled)
#         return

#     def is_enabled(self):
#         return self.enabled

#     def add_modified_ability(self, ability):
#         assert ability.__class__.__name__ == "Ability"

#         modified_ability = ModifiedAbility(patron = self.patron,
#                                            modified_ability_group = self,
#                                            ability = ability)
#         self.abilities.append(modified_ability)
#         return modified_ability

#     def get_martial_point_modifier(self):
#         return self.martial_point_modifier

#     def get_general_point_modifier(self):
#         return self.general_point_modifier
    
#     def get_lore_point_modifier(self):
#         return self.lore_point_modifier

#     def get_magical_point_modifier(self):
#         return self.magical_point_modifier

#     def get_successes_modifier(self):
#         return self.successes_modifier

#     def get_attempts_modifier(self):
#         return self.attempts_modifier

#     def get_failures_modifier(self):
#         return self.failures_modifier

#     #def get_point_modifier(self):
#     #    return self.lore_point_modifier

#     #def get_lore_point_modifier(self):
#     #    return self.lore_point_modifier

#     def is_enabled(self):
#         return self.enabled

#     def get_abilities(self):
#         return self.abilities

#     def get_filtered_abilities(self):
#         """
#         Returns a list of abilities that are enabled and not innate.
        
#         """
#         return [
#             ability for ability in self.abilities # ]
#             if ability.is_enabled()] ## FIXME
#             #if not ability.is_innate() and ability.is_enabled()] ## FIXME

    
#     def get_title(self):
#         return self.ability_group.get_title()

#     def __cmp__(self, other):
#         return cmp(self.ability_group, other.ability_group)
    

# class LevelProgressionData:
#     """
#     Information about going up a level for an Patron.

#     """

#     def __init__(self, fname):

#         # filename where this information is defined.
#         self.fname = fname

#         # this level number
#         self.level_number = None

#         # 
#         self.level_description = None

#         # hit points
#         self.level_stamina = None
#         self.level_stamina_refresh = None
#         self.level_health = None
#         self.level_health_refresh = None

#         # points gained.
#         self.level_lore = None
#         self.level_martial = None
#         self.level_general = None
#         self.level_magical = None

#         # resolve pool
#         self.level_resolve = None
#         self.level_resolve_refresh = None
        
#         # luck pool
#         self.level_fate = None
#         self.level_fate_refresh = None
        
#         # magic pool
#         self.level_magic_pool = None        
#         self.level_magic_refresh = None        
#         return

#     def get_level_number(self):
#         return self.level_number

#     def load(self, patron_node, fail_fast):        

#         # handle all the children
#         for child in list(patron_node):
        
#            tag = child.tag
#            if tag == "levelnumber":
#                if self.level_number is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_number = int(child.text.strip())

#            elif tag == "levelresolve":
#                if self.level_resolve is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_resolve = contents_to_string(child)
                   

#            elif tag == "levelresolverefresh":
#                if self.level_resolve_refresh is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_resolve_refresh = contents_to_string(child)

#            elif tag == "levelstamina":
#                if self.level_stamina is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_stamina = normalize_ws(child.text.strip())

#            elif tag == "levelstaminarefresh":
#                if self.level_stamina_refresh is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_stamina_refresh = normalize_ws(child.text.strip())

#            elif tag == "levelhealth":
#                if self.level_health is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                 self.level_health = normalize_ws(child.text.strip())

#            elif tag == "levelhealthrefresh":
#                if self.level_health_refresh is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                 self.level_health_refresh = normalize_ws(child.text.strip())

#            elif tag == "levellore":
#                if self.level_lore is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_lore = convert_str_to_int(child.text.strip())

#            elif tag == "levelmartial":
#                if self.level_martial is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_martial = convert_str_to_int(child.text.strip())

#            elif tag == "levelgeneral":
#                if self.level_general is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_general = convert_str_to_int(child.text.strip())

#            elif tag == "levelmagical":
#                if self.level_magical is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_magical = convert_str_to_int(child.text.strip())

#            elif tag == "leveldescription":
#                if self.level_description is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    if child.text is not None:
#                        self.level_description = child.text.strip()

#            elif tag == "levelmagicpool":
#                if self.level_magic_pool is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_magic_pool = contents_to_string(child)
                       
#            elif tag == "levelmagicrefresh":
#                if self.level_magic_refresh is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_magic_refresh = contents_to_string(child)

#            elif tag == "levelfate":
#                if self.level_fate is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_fate = contents_to_string(child)

#            elif tag == "levelfaterefresh":
#                if self.level_fate_refresh is not None:
#                    raise NonUniqueTagError(tag, self.fname, child.sourceline)
#                else:
#                    self.level_fate_refresh = contents_to_string(child)
                       
#            elif tag is COMMENT:
#                # ignore comments!
#                pass
           
#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, self.fname, child.sourceline))
#         return
            


# class LevelProgressionTable:
#     """
#     A list of level progression data for the Patron, one for each level.

#     """
#     def __init__(self, fname):
#         self.level_progression_data_list = []
#         self.fname = fname
#         return

#     def load(self, level_progression_table_node, fail_fast):        

#         # handle all the children
#         for child in list(level_progression_table_node):
        
#            tag = child.tag
#            if tag == "level":
#                level_progression_data = LevelProgressionData(self.fname)
#                level_progression_data.load(child, fail_fast)
#                self.level_progression_data_list.append(level_progression_data)

#            elif tag is COMMENT:
#                # ignore comments!
#                pass
           
#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, self.fname, child.sourceline))

#         self.level_progression_data_list.sort(key = lambda lpd: lpd.level_number)
#         return

#     def __iter__(self):
#         return iter(self.level_progression_data_list)




# class Tags:
#     """
#     A list of patron tags.

#     """
#     def __init__(self, fname):
#         self.tags = []
#         self.fname = fname
#         return

#     def load(self, patron_tags_node, fail_fast):        
#         # handle all the children
#         for child in list(patron_tags_node):
#            tag = child.tag
#            if tag == "tag":
#                tag = child.text.strip().lower()
#                self.tags.append(tag)
#            elif tag is COMMENT:
#                # ignore comments!
#                pass
#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, self.fname, child.sourceline))
#         self.tags.sort()
#         return

#     def __iter__(self):
#         return iter(self.tags)

#     def __str__(self):
#         return ", ".join(self.tags)

#     def __contains__(self, key):
#         return key.tag.lower() in self.tags


# class AttrBonus(object):
#     """
#     Modifier to attributes based on patron.

#     """

#     def __init__(self):
#         self.attribute = None
#         self.bonus = 0
#         return

#     def parse(self, fname, bonus_element):
#         for child in list(bonus_element):
#            tag = child.tag
#            if tag == "attr":
#                self.attribute = contents_to_string(child)

#            elif tag == "value":
#                try:
#                    self.bonus = convert_str_to_int(contents_to_string(child))
#                except ValueError as err:
#                    ValueError("%s (%s) File: %s Line: %s\n" % 
#                              (str(err), child.tag, fname, child.sourceline))
               
#            elif tag is COMMENT:
#                # ignore comments!
#                pass
        
#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, fname, child.sourceline))
#         return

#     def __setattr__(self, attr, value):
#         if attr == "bonus" and not isinstance(value, int):            
#             raise Exception("Readonly")
# 	object.__setattr__(self, attr, value)
#         return

    
#     def __str__(self):
#         return "{attribute:s} {bonus:+d}".format(**vars(self))


# class AttrLimitType:
#     MAX = "Max"
#     MIN = "Min"
    

# class AttrLimit:
#     """
#     Limit to attributes based on patron.

#     """

#     def __init__(self):
#         self.limit_type = None
#         self.attribute = None
#         self.limit = 0
#         return

#     def parse(self, fname, limit_type, limit_element):
#         self.limit_type = limit_type
        
#         for child in list(limit_element):
#            tag = child.tag

#            if tag == "attr":
#                self.attribute = contents_to_string(child)

#            elif tag == "value":
#                try:
#                    self.limit = convert_str_to_int(contents_to_string(child))
#                except ValueError as err:
#                    ValueError("%s (%s) File: %s Line: %s\n" % 
#                              (str(err), child.tag, fname, child.sourceline))                   

#            elif tag is COMMENT:
#                # ignore comments!
#                pass

#            else:
#                raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
#                                (child.tag, fname, child.sourceline))
#         return
        
#     def __str__(self):
#         return "{limit_type} {attribute:s}: {limit:d}".format(**vars(self))

        
    


class Patron:
    """
    Represents a Patron.
    
    """
    def __init__(self, fname):
        self.fname = fname # save for debugging?
        self.title = None
        self.patron_id = None
        # self.ancestor_ids = [None, ]
        self.description = None

        # Each patron has its own ability group.
        self.ability_group = None
        
        # self.ac = None
        # self.move = None
        # self.initiative = None
        # self.aspect_examples = None
        # self.starting_cash = None
        # self.starting_gear = None

        # self.height = None
        # self.weight = None
        # self.appearance = None
        # self.age = None

        # self.attr_bonuses = []
        # self.attr_limits = []

        # self.tags = Tags(fname)

        # each patron has a local copy of the ability-group tree with local modifications.
        # self.modified_abilities_lookup = {}
        # self.modified_ability_groups_lookup = {}
        # self.modified_ability_groups = []
        # for ability_group in ability_groups:
        #     modified_ability_group = ModifiedAbilityGroup(self, ability_group)
        #     self.modified_ability_groups.append(modified_ability_group)
        #     self.modified_ability_groups_lookup[ability_group.get_id()] = modified_ability_group

        #     for ability in ability_group.get_abilities():
        #         modified_ability = modified_ability_group.add_modified_ability(ability)
        #         self.modified_abilities_lookup[ability.get_id()] = modified_ability
        
        # # Sort by group name
        # self.modified_ability_groups.sort()

        # # update these after a load
        # self.innate_ability_levels = []
                
        # # what advantages you get at what levels.
        # self.level_progression_table = LevelProgressionTable(self.fname)        
        return

    # def get_attribute_limits_str(self):
    #     if len(self.attr_limits) == 0:
    #         attr_limits_str = "None"
    #     else:
    #         attr_limits_str = ", ".join([str(limit) for limit in self.attr_limits])
    #     return attr_limits_str

    # def get_attribute_bonus_str(self):
    #     if len(self.attr_bonuses) == 0:
    #         attr_bonus_str = "None"
    #     else:
    #         attr_bonus_str = ", ".join([str(bonus) for bonus in self.attr_bonuses])
    #     return attr_bonus_str
    

    # def get_modified_abilities(self):
    #     abilities = self.modified_abilities_lookup.values()

    #     def sort_fn(a, b):
    #         return cmp(a.get_title(), b.get_title())
        
    #     abilities.sort(sort_fn)
    #     return abilities
        
    
    # def has_magical_abilities(self):
    #     has_magical_abilities = False
    #     for modified_ability_group in self.modified_ability_groups:
    #         if modified_ability_group.get_family() == "Magic":
    #             for modified_ability in modified_ability_group:
    #                 if modified_ability.is_enabled():
    #                     has_magical_abilities = True
    #                     break
    #     return has_magical_abilities
    

    # def get_patron_specific_innate_ability_levels(self):
    #     """
    #     Returns the innate ability levels specific to this patron.

    #     """
    #     return [ ability_level for ability_level in self.innate_ability_levels if 
    #              ability_level.is_innate_for_this_patron() ]
 
    # def get_armour_class(self):
    #     return self.ac

    # def get_move(self):
    #     return self.move

    # def get_initiative_bonus(self):
    #     return self.initiative

    # def get_modified_ability(self, ability_id):
    #     return self.modified_abilities_lookup[ability_id]

    # def get_groups(self):
    #     return self.modified_ability_groups

    # def get_filtered_groups(self):
    #     """
    #     Return a list of groups with abilities the patron can actually take.

    #     """
    #     # return [
    #     #     group for group in self.modified_ability_groups
    #     #     if len(group.get_filtered_abilities()) > 0 ]
    #     return [
    #         group for group in self.modified_ability_groups   ## FIXME: filter disabled?
    #         if len(group.get_filtered_abilities()) > 0 ]

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description
        
    # def has_tags(self):
    #     return len(self.tags) > 0

    # def get_tags_str(self):
    #     return ", ".join(self.tags)

    # def get_starting_gear(self):
    #     return self.starting_gear

    # def get_starting_cash(self):
    #     return self.starting_cash

    # def get_initiative(self):
    #     return self.initiative
    
    # def get_level_progression_table(self):
    #     return self.level_progression_table

    def get_id(self):
        return self.patron_id

    def load(self, patron_node, ability_groups, fail_fast):
        try:
            self._load(patron_node, fail_fast)

            # # sort the ability levels
            # self.innate_ability_levels.sort(key = lambda mal: mal.get_title())

            # # update the innate abilities
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

            # # update the enabled flag in all the ability groups, abilities and levels
            # # (it might be out of date here)
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
            print "Problem trying to parse patron file: %s" % self.fname
            raise

        # after we've loaded all the archertype ability information
        # go through and set the innate information for prerequisites
        #self.set_innate_abilities() ###########################################
        # for ability in self.modified_abilities_lookup.values():
        #     for ability_level in ability:
        #         ability_level.check_consistency()
        return True


    #def _set_ability_prereqs_innate_for_innate_abilities(self):
    # def set_innate_abilities(self):
    #     """
    #     If an ability is innate and it has ability prerequisites then we 
    #     have to make those prerequisite abilities innate as well.

    #     We have to do this after we've loaded all the modified abilities so
    #     we can find change them.

    #     """
    #     for ability_group in self.modified_ability_groups:
    #         for ability in ability_group.get_abilities():
    #             if not ability.is_enabled():
    #                 continue
    #             for ability_level in ability:
    #                 #if ability_level.innate_flag:
    #                     ability_level.set_innate()
    #     return


    def _load(self, patron_node, fail_fast):        

        # handle all the children
        for child in list(patron_node):
        
           tag = child.tag
           if tag == "patrontitle":
               if self.title is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.title = child.text.strip() 

           elif tag == "patronid":
               if self.patron_id is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.patron_id = child.text.strip() 

           elif tag == "patronac":
               if self.ac is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.ac = child.text.strip()

           elif tag == "abilitygroup":
               if self.ability_group is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.ability_group = AbilityGroup(self.fname)
                   self.ability_group.load(child)
                   
           # elif tag == "patronmove":
           #     if self.move is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.move = child.text.strip() 

           # elif tag == "inheritance":
           #     self._load_inheritance(inheritance = child)

           elif tag == "patrondescription":
               if self.description is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.description = children_to_string(child)

           # elif tag == "patroninitiative":
           #     if self.initiative is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #         #raise Exception("Only one patroninitiative per file.")
           #     else:
           #         self.initiative = convert_str_to_int(child.text)

           # elif tag == "startingcash":
           #     if self.starting_cash is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.starting_cash = child.text

           # elif tag == "startinggear":
           #     if self.starting_gear is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.starting_gear = normalize_ws(child.text)

           # elif tag == "height":
           #     if self.height is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.height = parse_measurement_to_str(self.fname, child)

           # elif tag == "weight":
           #     if self.weight is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.weight = parse_measurement_to_str(self.fname, child)

           # elif tag == "appearance":
           #     if self.appearance is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.appearance = normalize_ws(child.text)

           # elif tag == "age":
           #     if self.age is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.age = normalize_ws(child.text)

           # elif tag == "aspectexamples":
           #     if self.aspect_examples is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.aspect_examples = child.text

           # elif tag == "patrontags":
           #     self.tags.load(child, fail_fast)

           # elif tag == "levelprogressiontable":
           #     self.level_progression_table.load(child, fail_fast)

           # elif tag == "abilitymodifiers":
           #     self._load_ability_modifiers(child)

           # elif tag == "attrbonus":
           #     bonus = AttrBonus()
           #     bonus.parse(self.fname, child)
           #     self.attr_bonuses.append(bonus)

           # elif tag == "attrmax":
           #     attr_max = AttrLimit()
           #     attr_max.parse(self.fname, AttrLimitType.MAX, child)
           #     self.attr_limits.append(attr_max)

           # elif tag == "attrmin":
           #     attr_min = AttrLimit()
           #     attr_min.parse(self.fname, AttrLimitType.MIN, child)
           #     self.attr_limits.append(attr_min)

           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, self.fname, child.sourceline))
        return
            

    # def _load_inheritance(self, inheritance):
    #     """
    #     Parse the <inheritance> element and its children.

    #     """
    #     # handle all the children
    #     for child in list(inheritance):
    #        tag = child.tag

    #        if tag == "ancestor":
    #            ancestor_id = child.text.strip()
    #            self.ancestors.append(ancestor_id)

    #        elif tag is COMMENT:               
    #            pass # ignore comments!

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))
    #     return


    # def _load_innate_ability_modifier(self, innate_node):
    #     ability_id = None
    #     ability_level = None
        
    #     # handle all the children
    #     for child in list(innate_node):
    #        tag = child.tag

    #        if tag == "abilityid":
    #            if ability_id is not None:
    #                raise Exception("Only one id per ability modifier!")
    #            else:
    #                ability_id = child.text.strip()    

    #        elif tag == "level":
    #            ability_level = convert_str_to_int(child.text)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))

    #     if ability_id not in self.modified_abilities_lookup:
    #         raise Exception("Unknown ability id: '%s' in patron file: %s Line: %s\n" % 
    #                         (ability_id, self.fname, child.sourceline))
    #     else:        
    #         ability = self.modified_abilities_lookup[ability_id]
        
    #     ability_level = ability.get_modified_ability_level(ability_level)
    #     ability_level.set_innate()
    #     return
        

    # def _load_ability_modifiers(self, ability_modifiers):
    #     """
    #     Load a bunch of ability modifiers.

    #     """
    #     # handle all the children
    #     for child in list(ability_modifiers):
    #        tag = child.tag

    #        if tag == "abilitymodifier":
    #            self._load_ability_modifier(child)

    #        elif tag == "abilitygroupmodifier":
    #            self._load_ability_group_modifier(child)

    #        elif tag == "disable":
    #            self.set_enabled(child, False)

    #        elif tag == "enable":
    #            self.set_enabled(child, True)

    #        elif tag == "innate":               
    #            self._load_innate_ability_modifier(child)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))
    #     return
           

    # def _load_ability_modifier(self, ability_modifier):
    #     ability_id = None
    #     lore_point_modifier = 0
    #     martial_point_modifier = 0
    #     general_point_modifier = 0
    #     magical_point_modifier = 0
    #     successes_modifier = 0
    #     attempts_modifier = 0
    #     failures_modifier = 0
        
    #     # parse ability level modifiers last.
    #     ability_level_modifier_elements = []

    #     # handle all the children
    #     for child in list(ability_modifier):
    #        tag = child.tag

    #        if tag == "abilityid":
    #            if ability_id is not None:
    #                raise Exception("Only one id per ability modifier!")
    #            else:
    #                ability_id = child.text.strip()               

    #        elif tag == "lorepointmodifier":
    #            lore_point_modifier = convert_str_to_int(child.text)

               
    #        elif tag == "martialpointmodifier":
    #            martial_point_modifier = convert_str_to_int(child.text)
               
    #        elif tag == "generalpointmodifier":
    #            self.general_point_modifier = convert_str_to_int(child.text)

    #        elif tag == "magicalpointmodifier":
    #            self.magical_point_modifier = convert_str_to_int(child.text)

    #        elif tag == "abilitylevelmodifier":
    #            ability_level_modifier_elements.append(child)

    #        elif tag == "successesmodifier":
    #            successes_modifier = convert_str_to_int(child.text)

    #        elif tag == "failuresmodifier":
    #            failures_modifier = convert_str_to_int(child.text)

    #        elif tag == "attemptsmodifier":
    #            attempts_modifier = convert_str_to_int(child.text)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))
           
    #     if ability_id not in self.modified_abilities_lookup:
    #         raise Exception("UNKNOWN ABILITY (%s) File: %s Line: %s\n" % 
    #                            (ability_id, self.fname, child.sourceline))

    #     modified_ability = self.modified_abilities_lookup[ability_id]
    #     modified_ability.martial_point_modifier = martial_point_modifier
    #     modified_ability.lore_point_modifier = lore_point_modifier
    #     modified_ability.general_point_modifier = general_point_modifier
    #     modified_ability.magical_point_modifier = magical_point_modifier
    #     modified_ability.successes_modifier = successes_modifier
    #     modified_ability.failures_modifier = failures_modifier
    #     modified_ability.attempts_modifier = attempts_modifier

    #     # handle
    #     for child in ability_level_modifier_elements:
    #         modified_ability.load_ability_level_modifier(child)
        
    #     return


    # def _load_ability_group_modifier(self, ability_group_modifier):

    #     ability_group_id = None
    #     lore_point_modifier = 0
    #     martial_point_modifier = 0
    #     general_point_modifier = 0
    #     magical_point_modifier = 0
    #     successes_modifier = 0
    #     attempts_modifier = 0
    #     failures_modifier = 0
        
    #     # handle all the children
    #     for child in list(ability_group_modifier):
    #        tag = child.tag

    #        if tag == "abilitygroupid":
    #            if ability_group_id is not None:
    #                raise Exception("Only one id per ability group modifier!")
    #            else:
    #                ability_group_id = child.text.strip()

    #                if ability_group_id not in self.modified_ability_groups_lookup:
    #                    raise Exception("UNKNOWN ABILITY GROUP ID (%s) File: %s Line: %s\n" % 
    #                                    (ability_group_id, self.fname, child.sourceline))

    #        elif tag == "lorepointmodifier":
    #            lore_point_modifier = convert_str_to_int(child.text)
               
    #        elif tag == "martialpointmodifier":
    #            martial_point_modifier = convert_str_to_int(child.text)
               
    #        elif tag == "generalpointmodifier":
    #            general_point_modifier = convert_str_to_int(child.text)
               
    #        elif tag == "magicalpointmodifier":
    #            magical_point_modifier = convert_str_to_int(child.text)

    #        elif tag == "successesmodifier":
    #            successes_modifier = convert_str_to_int(child.text)

    #        elif tag == "failuresmodifier":
    #            failures_modifier = convert_str_to_int(child.text)

    #        elif tag == "attemptsmodifier":
    #            attempts_modifier = convert_str_to_int(child.text)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))

    #     modified_ability_group = self.modified_ability_groups_lookup[ability_group_id]
    #     modified_ability_group.lore_point_modifier = lore_point_modifier
    #     modified_ability_group.martial_point_modifier = martial_point_modifier
    #     modified_ability_group.general_point_modifier = general_point_modifier
    #     modified_ability_group.magical_point_modifier = magical_point_modifier
    #     modified_ability_group.successes_modifier = successes_modifier
    #     modified_ability_group.attempts_modifier = attempts_modifier
    #     modified_ability_group.failures_modifier = failures_modifier

    #     ## assert self.ability_id is not None
    #     ## return ability_modifier
    #     return


    # def set_enabled(self, children, enabled):
        
    #     # handle all the children
    #     for child in list(children):
    #        tag = child.tag

    #        if tag == "abilityid":
    #            ability_id = child.text.strip()

    #            if ability_id not in self.modified_abilities_lookup:
    #                raise Exception("UNKNOWN ABILITY ID (%s) File: %s Line: %s\n" % 
    #                                (ability_id, self.fname, child.sourceline))
               
    #            modified_ability = self.modified_abilities_lookup[ability_id]
    #            modified_ability.set_enabled(enabled)

    #        elif tag == "abilitygroupid":
    #            ability_group_id = child.text.strip()

    #            if ability_group_id not in self.modified_ability_groups_lookup:
    #                raise Exception("UNKNOWN ABILITY GROUP ID (%s) File: %s Line: %s\n" % 
    #                                (ability_group_id, self.fname, child.sourceline))
               
    #            modified_ability_group = self.modified_ability_groups_lookup[ability_group_id]
    #            modified_ability_group.set_enabled(enabled)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass

    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))
    #     return
    

class Patrons:
    """
    A list of all enabled patrons.

    """
    def __init__(self):
        self.patrons = []
        self.patron_lookup = {}
        return

    def __iter__(self):
        return iter(self.patrons)

    def __getitem__(self, key):
         return self.patron_lookup[key]

 
    def load_patron_from_xml(self, xml_fname, ability_groups, fail_fast):
        """
        Load a patron in an xml file.

        """
        #patrons_in_file = []

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
        patron = Patron(xml_fname)
        patron.load(root, ability_groups, fail_fast)
        return patron

    
    def load(self, patrons_dir, ability_groups, fail_fast):
        """
        Load all the patrons in all the xml files in the docs_dir.

        """
        
        for xml_fname in listdir(patrons_dir):
            fname = basename(xml_fname)

            if not xml_fname.endswith(".xml"):
                continue

            full_xml_fname = join(patrons_dir, xml_fname)
            patron = self.load_patron_from_xml(
                full_xml_fname,
                ability_groups,
                fail_fast)

            # check for duplicates
            key = patron.get_id()
            if key in self.patron_lookup:
                raise Exception("The same patron key: %s is used in two patrons! "
                                "See file: %s and file: %s" % (
                                    key,
                                    self.patron_lookup[key].fname,
                                    xml_fname))

            # add to the list of patrons
            self.patron_lookup[key] = patron
            self.patrons.append(patron)
        return


if __name__ == "__main__":

    src_dir = abspath(join(dirname(__file__)))
    root_dir = abspath(join(src_dir, ".."))
    #sys.path.append(src_dir)

    # from abilities import AbilityGroups
    ability_groups = AbilityGroups()
    # ability_groups_dir = join(root_dir, "abilities")
    # ability_groups.load(ability_groups_dir, fail_fast = True)
    # #abilities = ability_groups.get_abilities()

    patrons = Patrons()
    patrons_dir = join(root_dir, "patrons")
    patrons.load(patrons_dir, ability_groups, fail_fast = True)
    #build_dir = join(root_dir, "build")
    #patrons.write_abilities_xml_to_dir(build_dir)

    for patron in patrons:
        print patron.get_title()

        #if "Outrider" not in patron.get_title():
        #    continue
        
        print("Patron: %s" % patron.get_title())        

        # for patron in patron.modified_ability_groups:
        #     if "ocial" not in ability_group.get_title():
        #         continue

        #     #print("\t%s" % ability_group.get_title())
        #     for ability in ability_group:

        #         if "Negotiate" not in ability.get_title():
        #             continue
                
        #         print("\t\t%s" % ability.get_title())
        #         print("\t\tHighest innate level %s" % ability.get_highest_innate_level())
                
        #         for mal in ability.get_levels():
        #             print("\t\t\t%s %s" % (mal.get_title(), mal.get_total_point_cost()))
        #             print("\t\t\tIS INNATE %s" % mal.is_innate(d = True))
        #             print("\t\t\t\tRecommended: %s" % mal.is_recommended())
        
        #             print("\t\t\t\tArch Innate: %s" %
        #                   mal.is_innate_for_this_patron())