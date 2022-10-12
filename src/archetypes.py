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
from abilities import AbilityRank


DEFAULT_GENDER = "Choose whatever gender you want."


class NonUniqueTagError(Exception):
    """Expecting at most one of this sort of tag."""

    def __init__(self, tag, fname, line_number):
        super(NonUniqueTagError, self).__init__(
            "Only one tag: %s per file. %s:%s" % (tag, fname, line_number))
        return

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
        self.level_description = ""

        # hit points
        self.level_stamina = None
        self.level_health = None
        self.level_health_refresh = None

        # level up ability gains and promotions
        self.level_abilities = ""
        self.level_promotions = ""

        # mettle pool
        self.level_mettle = None
        self.level_mettle_refresh = None
        
        # luck pool
        self.level_luck = None
        self.level_luck_refresh = None
        
        # magic pool
        self.level_magic = None        
        self.level_magic_refresh = None

        self.tags = []
        return

    def get_level_number(self):
        return self.level_number

    def load_level_abilities(self, node):
        self.level_abilities = contents_to_string(node)

    def load_level_promotions(self, node):
        self.level_promotions = contents_to_string(node)

    def load(self, archetype_node, fail_fast):
        # handle all the children
        for child in list(archetype_node):
        
           tag = child.tag
           if tag == "levelnumber":
               if self.level_number is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_number = int(child.text.strip())

           elif tag == "levelmettle":
               if self.level_mettle is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_mettle = contents_to_string(child)                   

           elif tag == "levelmettlerefresh":
               if self.level_mettle_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_mettle_refresh = contents_to_string(child)

           elif tag == "levelstamina":
               if self.level_stamina is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_stamina = normalize_ws(child.text.strip())

           # elif tag == "levelstaminarefresh":
           #     if self.level_stamina_refresh is not None:
           #         raise NonUniqueTagError(tag, self.fname, child.sourceline)
           #     else:
           #         self.level_stamina_refresh = normalize_ws(child.text.strip())

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
               if self.level_description != "":
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.level_description = contents_to_string(child)

           elif tag == "levelabilities":
               if len(self.level_abilities) > 0:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_abilities(child)

           elif tag == "levelpromotions":
               if len(self.level_promotions) > 0:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_promotions(child)

           elif tag == "levelmagicpool":
               if self.level_magic is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_magic = contents_to_string(child)
                       
           elif tag == "levelmagicrefresh":
               if self.level_magic_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_magic_refresh = contents_to_string(child)

           elif tag == "levelluck":
               if self.level_luck is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_luck = contents_to_string(child)

           elif tag == "levelluckrefresh":
               if self.level_luck_refresh is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.level_luck_refresh = contents_to_string(child)
                       
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
        self.move_distance = None
        self.aspect_examples = None
        self.starting_cash = None
        self.starting_gear = None

        # text describing how to initially set primary abilities for this archetype
        self.primary_abilities = None
        
        # text describing the abilities that all members of the archetype initially get.
        self.initial_abilities = None
        
        self.bio = None        
        self.height = None
        self.weight = None
        self.age = None
        self.gender = DEFAULT_GENDER

        self.tags = []
        
        # update these after a load
        self.innate_ability_ranks = []
                
        # what advantages you get at what levels.
        self.level_progression_table = LevelProgressionTable(self.fname)        
        return

    def get_progression_data_for_level(self, level):
        return self.level_progression_table.level_progression_data_list[level]

    def get_bio(self):
        return self.bio

    def get_attribute_limits_str(self):
        if len(self.attr_limits) == 0:
            attr_limits_str = "None"
        else:
            attr_limits_str = ", ".join([str(limit) for limit in self.attr_limits])
        return attr_limits_str

    # def get_modified_abilities(self):
    #     # abilities = self.modified_abilities_lookup.values()

    #     # def sort_fn(a, b):
    #     #     return cmp(a.get_title(), b.get_title())
        
    #     # abilities.sort(sort_fn)
    #     # return abilities
    #     return []        

    def load_tags(self, tags_node, fail_fast):
        for child in list(tags_node):
            if child.tag is not COMMENT:
                #tag = child.tag[:-1]
                tag = child.tag
                self.tags.append(tag)
        self.tags.sort()
        return
    
    # def load_tags(self, tags_node, fail_fast):        
    #     # handle all the children
    #     for child in list(tags_node):
    #        tag = child.tag
    #        if tag == "tag":
    #            tag = child.text.strip().lower()
    #            self.tags.append(tag)
    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass
    #        else:
    #            raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
    #                            (child.tag, self.fname, child.sourceline))
    #     self.tags.sort()
    #     return

    
    def has_magical_abilities(self):
        has_magical_abilities = False
        for modified_ability_group in self.modified_ability_groups:
            if modified_ability_group.get_family() == "Magic":
                for modified_ability in modified_ability_group:
                    if modified_ability.is_enabled():
                        has_magical_abilities = True
                        break
        return has_magical_abilities
    

    def get_archetype_specific_innate_ability_ranks(self):
        """
        Returns the innate ability ranks specific to this archetype.

        """
        return [ ability_rank for ability_rank in self.innate_ability_ranks if 
                 ability_rank.is_innate_for_this_archetype() ]
 
    def get_move_distance(self):
        return self.move_distance

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
        
    def get_primary_abilities(self):
        return self.primary_abilities

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

            # sort the ability ranks
            self.innate_ability_ranks.sort(key = lambda mal: mal.get_title())

            # update the innate abilities
            # for ability in list(self.modified_abilities_lookup.values()):
            #     ranks = ability.get_ranks()
            #     max_rank = None
            #     for rank in ranks:
            #         if not rank.is_innate():
            #             continue

            #         if (max_rank is None or 
            #             (max_rank.get_rank_number() < rank.get_rank_number())):
            #             max_rank = rank

            #     if max_rank is not None:
            #         self.innate_ability_ranks.append(max_rank)

            # update the enabled flag in all the ability groups, abilities and ranks
            # (it might be out of date here)
            # for ability_group in self.modified_ability_groups:

            #     # if a group is disabled all it's ranks and abilities are also disabled.
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

            #             # also an ability is disabled if all its ranks are.
            #             all_ability_ranks_disabled = True
            #             for ability_rank in ability:
            #                 if ability_rank.is_enabled():
            #                     all_ability_ranks_disabled = False
            #                     break

            #                 if all_ability_ranks_disabled:
            #                     ability.set_enabled(False)
        except:
            print("Problem trying to parse archetype file: %s" % self.fname)
            raise

        # after we've loaded all the archertype ability information
        # go through and set the innate information for prerequisites
        #self.set_innate_abilities() ###########################################
        # for ability in self.modified_abilities_lookup.values():
        #     for ability_rank in ability:
        #         ability_rank.check_consistency()

        self.check_consistency()                
        return True
    

    def check_consistency(self):        
        # if self.initial_abilities is None:
        #     raise Exception("Missing 'initial_abilities' in file: %s" % self.fname)
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

           elif tag == "archetypemovedistance":
               if self.move_distance is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.move_distance = child.text.strip() 

           elif tag == "inheritance":
               self._load_inheritance(inheritance = child)

           elif tag == "archetypedescription":
               if self.description is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.description = children_to_string(child)

           elif tag == "archetypeprimaryabilities":
               if self.primary_abilities is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.primary_abilities = contents_to_string(child)

           elif tag == "archetypeinitialabilities":
               if self.initial_abilities is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.initial_abilities = contents_to_string(child)

           elif tag == "archetypebio":
               if self.bio is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.bio = children_to_string(child)
    
           elif tag == "archetypeinitiative":
               if self.initiative is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
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

           elif tag == "age":
               if self.age is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.age = normalize_ws(child.text)

           elif tag == "gender":
               if self.gender != DEFAULT_GENDER:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.gender = normalize_ws(child.text)

           elif tag == "aspectexamples":
               if self.aspect_examples is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.aspect_examples = child.text

           elif tag == "archetypetags":
               self.load_tags(child, fail_fast)

           elif tag == "levelprogressiontable":
               self.level_progression_table.load(child, fail_fast)

           elif tag == "attrbonus":
               bonus = AttrBonus()
               bonus.parse(self.fname, child)
               self.attr_bonuses.append(bonus)

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
        Load all the archetypes in all the xml files in the archetypes_dir.

        """
        for xml_fname in listdir(archetypes_dir):
            fname = basename(xml_fname)          

            if not xml_fname.endswith(".xml"):
                continue

            # Files starting with .# are created by emacs.. just ignore them (they're modified but not saved).
            if xml_fname.startswith(".#"):
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
        # print("initial abilities: %s\n" % archetype.get_initial_abilities())
        # for ability_group in archetype.modified_ability_groups:
        #     #if "onster" not in ability_group.get_title():
        #     #   continue            

        #     #print("\t%s" % ability_group.get_title())
        #     # for ability in ability_group:

        #     #     #if "Negotiate" not in ability.get_title():
        #     #     #    continue
                
        #     #     print("\t\t%s" % ability.get_title())
        #     #     print("\t\tHighest innate rank %s" % ability.get_highest_innate_rank())
                
        #     #     for mal in ability.get_rankns():
        #     #         print("\t\t\t%s %s" % (mal.get_title(), mal.get_total_point_cost()))
        #     #         print("\t\t\tIS INNATE %s" % mal.is_innate(d = True))
        #     #         print("\t\t\t\tRecommended: %s" % mal.is_recommended())        
        #     #         print("\t\t\t\tArch Innate: %s" %
        #     #               mal.is_innate_for_this_archetype())
        #     #         print("\t\t\t\tEnabled?: %s" %
        #     #               mal.is_enabled())
