#!/usr/bin/env python
#from os.path import abspath, join, splitext, dirname, exists, basename
from os.path import join
from os import listdir

from parser_utils import parse_xml, validate_xml
#, node_to_string, COMMENT, children_to_string



class MonsterGroups:


    def __init__(self):
        self.monster_groups = []
        return

    def load(self, monsters_dir, fail_fast):
        
        # load all the ability groups
        for xml_fname in listdir(monsters_dir):
            if not xml_fname.endswith(".xml"):
                continue

            if xml_fname.startswith(".#"):
                continue
            
            xml_fname = join(monsters_dir, xml_fname)
            monster_group = MonsterGroup(xml_fname)
            if not monster_group.validate() and fail_fast:
                return False
            monster_group.load()

            self.monster_groups.append(monster_group)

            # # populate the ability_id -> ability lookup table
            # for ability in ability_group.get_abilities():
            #     self.ability_lookup[ability.get_id()] = ability

        # # inform each ability about abilities that require it as a prerequisite
        # for ability_group in self.ability_groups:
        #     for ability in ability_group.get_abilities():

        #         for ability_level in ability.get_levels():

        #             for prereq in ability_level.get_ability_level_prereqs():
        #                 # for prereq_ability_level_id in ability_level.get_prerequisite_ids():

        #                 #if prereq_ability_level_id is None:
        #                 #    continue

        #                 # reqister this ability level with any prerequisites it might have
        #                 prereq_ability_level = AbilityLevel.get_level(prereq.ability_level_id)
                        
        #                 if prereq_ability_level is None:
        #                     raise Exception(
        #                         ("No ability level matches prereq key: %s "
        #                          "for ability: %s") % 
        #                         (prereq_ability_level_id, ability_level.get_title()))
        #                 prereq_ability_level.add_dependency(ability_level.get_id())

        # sort the groups
        self.monster_groups.sort()
        return True
    

class MonsterGroup:

    def __init__(self, xml_fname):
        self.xml_fname = xml_fname
        self.doc = parse_xml(xml_fname)
        self.info = None
        return

    def validate(self):
        #cls = self.__class__
        valid = True
        error_log = validate_xml(self.doc)
        if error_log is not None:
            print("Errors (XSD)!")
            valid = False
            print("\t%s" % error_log)
        return valid
    

    def load(self):
        root = self.doc.getroot()

        # check it's the right sort of element
        if root.tag != "monstergroup":
            raise Exception("UNEXPECTED TAG (%s) %s in file: %s\n" %
                            (root.tag, str(root), self.xml_fname))
        
        # handle all the children of the monster group
        for child in list(root):
        
           tag = child.tag
           if tag == "monstergroupinfo":
               if self.info is not None:
                   raise Exception("Only one abilitygroupinfo per file.")
               else:
                   self.info = MonsterGroupInfo(self.fname)
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
        


class Monster:

    def __init__(self):
        self.name = None
        return



if __name__ == "__main__":

    monster_groups = MonsterGroups()
    monster_groups_dir = join(root_dir, "monsters")
    monster_groups.load(monster_groups_dir, fail_fast = True)
    
    # build_dir = join(root_dir, "build")
    # #ability_groups.draw_all_skill_trees(build_dir)
    # #ability_groups.draw_skill_tree(build_dir)
    # #ability_groups.draw_skill_tree2(build_dir)

    # for ability_group in ability_groups:
    #     print(ability_group.get_title())

    #     for ability in ability_group:

    #         if "eering" not in ability.get_title():
    #             continue
            
    #         print("\t%s" % ability.get_title())
    #         print("\t\t\tAbility Class: %s" % ability.get_ability_class())
    #         print("\t\t\tAbility Desc: %s" % ability.description)
    #         #print("\t\t\tAbility Class: %s" % ability.get_ability_class())
    #         #print("\t\t\t\t: %s" % ability.get_ability_class())
            
    #         for ability_level in ability.get_levels():
    #             print("\t\t\t\t%s" % ability_level.get_title())
    #             print("\t\t\t\t%s" % ability_level.check)
    #             print("\t\t\t\t%s" % ability_level.description)
    #         #    #print("\t\t\tLore: %s" % ability_level.get_default_lore())



