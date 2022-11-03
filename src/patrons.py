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

"""
 
 sponge.
 oil black and brown
 inks?

      {% from "docs/macro_ability.xml" import build_ability with context %}

      
      {% for ability in ability_group.get_abilities()%}

      <subsectiontitle>
	{{ ability.get_title() }} {{ ability.get_ability_class_symbol() }}
      </subsectiontitle>    

      {{ build_ability(ability) }}
      {% endfor %}

"""

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
            print("Problem trying to parse patron file: %s" % self.fname)
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
        print(patron.get_title())

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
