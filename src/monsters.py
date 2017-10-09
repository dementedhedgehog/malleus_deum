#!/usr/bin/env python
#from os.path import abspath, join, splitext, dirname, exists, basename
from os.path import join
from os import listdir

from utils import parse_xml, validate_xml, children_to_string, contents_to_string
#, node_to_string, COMMENT



# class MonsterGroups:


#     def __init__(self):
#         self.monster_groups = []
#         return

#     def load(self, monsters_dir, fail_fast):
        
#         # load all the monster groups
#         for xml_fname in listdir(monsters_dir):
#             if not xml_fname.endswith(".xml"):
#                 continue

#             if xml_fname.startswith(".#"):
#                 continue
            
#             xml_fname = join(monsters_dir, xml_fname)
#             monster_group = MonsterGroup(xml_fname)
#             if not monster_group.validate() and fail_fast:
#                 return False
#             monster_group.load()

#             self.monster_groups.append(monster_group)

#             # # populate the monster_id -> monster lookup table
#             # for monster in monster_group.get_monsters():
#             #     self.monster_lookup[monster.get_id()] = monster

#         # # inform each monster about monsters that require it as a prerequisite
#         # for monster_group in self.monster_groups:
#         #     for monster in monster_group.get_monsters():

#         #         for monster_level in monster.get_levels():

#         #             for prereq in monster_level.get_monster_level_prereqs():
#         #                 # for prereq_monster_level_id in monster_level.get_prerequisite_ids():

#         #                 #if prereq_monster_level_id is None:
#         #                 #    continue

#         #                 # reqister this monster level with any prerequisites it might have
#         #                 prereq_monster_level = MonsterLevel.get_level(prereq.monster_level_id)
                        
#         #                 if prereq_monster_level is None:
#         #                     raise Exception(
#         #                         ("No monster level matches prereq key: %s "
#         #                          "for monster: %s") % 
#         #                         (prereq_monster_level_id, monster_level.get_title()))
#         #                 prereq_monster_level.add_dependency(monster_level.get_id())

#         # sort the groups
#         self.monster_groups.sort()
#         return True
    

class MonsterGroups:
    """
    A list of all enabled skills.

    """
    def __init__(self):
        self.monster_groups = []
        self.monster_lookup = {}
        return

    def __iter__(self):
        return iter(self.monster_groups)

    
    def load(self, monsters_dir, fail_fast):
        
        # load all the monster groups
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

            # populate the monster_id -> monster lookup table
            for monster in monster_group.get_monsters():
                self.monster_lookup[monster.get_id()] = monster

        # inform each monster about monsters that require it as a prerequisite
        # for monster_group in self.monster_groups:
        #     for monster in monster_group.get_monsters():

        #         for monster_level in monster.get_levels():

        #             for prereq in monster_level.get_monster_level_prereqs():
        #                 # for prereq_monster_level_id in monster_level.get_prerequisite_ids():

        #                 #if prereq_monster_level_id is None:
        #                 #    continue

        #                 # reqister this monster level with any prerequisites it might have
        #                 prereq_monster_level = MonsterLevel.get_level(prereq.monster_level_id)
                        
        #                 if prereq_monster_level is None:
        #                     raise Exception(
        #                         ("No monster level matches prereq key: %s "
        #                          "for monster: %s") % 
        #                         (prereq_monster_level_id, monster_level.get_title()))
        #                 prereq_monster_level.add_dependency(monster_level.get_id())

        # sort the groups
        self.monster_groups.sort()

        return True

    def get_monster_level_by_id(self, monster_level_id):
        return monster_level_lookup[monster_level_id]

    def get_monster_groups(self):
        return self.monster_groups
    
    def __getitem__(self, key):
        return self.monster_groups[key]

    

class MonsterGroupInfo:
    """
    A group of monsters
    
    """
    # set of all monster ids we've seen
    # there should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.title = None
        self.monster_group_id = None
        self.description = None
        self.family = None # one of Combat, Mundane or Magic.
        return

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def load(self, monster_group_info_element):

        # check it's the right sort of element
        if monster_group_info_element.tag != "monstergroupinfo":
            raise Exception("UNKNOWN (%s) %s\n" % (monster_group_info_element.tag,
                                                   str(monster_group_info_element)))
        self._load(monster_group_info_element)
        return


    def _load(self, monster_group_info_element):
        
        # handle all the children
        for child in list(monster_group_info_element):
        
           tag = child.tag
           if tag == "monstergrouptitle":
               if self.title is not None:
                   raise Exception("Only one monstergrouptitle per file.")
               else:
                   self.title = child.text.strip() 

           elif tag == "monstergroupid":
               if self.monster_group_id is not None:
                   raise Exception("Only one monstergroupid per monster. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   monster_group_id = child.text
                   monster_group_location = "%s:%s" % (self.fname, child.sourceline)
                   if monster_group_id in self._ids:
                       previous_location = self._ids[monster_group_id]
                       raise Exception("Monster group id: '%s' appears in two places %s and %s"
                                       % (monster_group_id,
                                          monster_group_location,
                                          previous_location))
                   else:
                        self._ids[monster_group_id] = monster_group_location

                   # save the id!
                   self.monster_group_id = monster_group_id
                   
           elif tag == "monstergroupfamily":
                self.family = child.text
                assert self.family in ("Mundane", "Combat", "Magic")
                

           elif tag == "monstergroupdescription":
               if self.description is not None:
                   raise Exception("Only one monstergroupdescription per file.")
               else:                   
                   self.description = contents_to_string(child)
                   # children_to_string(child)
                   #print "---"
                   #print self.description
                   #print contents_to_string(child)
                   #print child

           elif tag is COMMENT:
               pass # ignore comments!

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

           print(self.description)
        return

# class MonsterGroup:

#     def __init__(self, xml_fname):
#         self.fname = xml_fname
#         self.doc = parse_xml(xml_fname)
#         self.info = None
#         self.monsters = []
#         return

#     def validate(self):
#         #cls = self.__class__
#         valid = True
#         error_log = validate_xml(self.doc)
#         if error_log is not None:
#             print("Errors (XSD)!")
#             valid = False
#             print("\t%s" % error_log)
#         return valid
    

#     def load(self):
#         root = self.doc.getroot()

#         # check it's the right sort of element
#         if root.tag != "monstergroup":
#             raise Exception("UNEXPECTED TAG (%s) %s in file: %s\n" %
#                             (root.tag, str(root), self.xml_fname))
        
#         # handle all the children of the monster group
#         for child in list(root):
        
#            tag = child.tag
#            if tag == "monstergroupinfo":
#                if self.info is not None:
#                    raise Exception("Only one monstergroupinfo per file.")
#                else:
#                    self.info = MonsterGroupInfo(self.fname)
#                    self.info.load(child)

#            elif tag == "monster":
#                monster = Monster(self.fname)
#                monster.load(child)
#                self.monsters.append(monster)

#            elif tag is COMMENT:               
#                pass # ignore comments!

#            else:
#                raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
#         return


class MonsterGroup:
    xsd_schema = None

    def __init__(self, fname):
        self.fname = fname
        self.doc = parse_xml(fname)
        self.info = None
        self.monsters = []
        return

    def get_description(self):        
        return self.info.get_description()

    def get_title(self):
        return self.info.title
        
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
        return iter(self.monsters)

    def get_id(self):
        return self.info.monster_group_id

    def get_info(self):
        return self.info

    def get_title(self):
        return self.info.get_title()

    def get_description(self):
        return self.info.get_description()
    
    def get_monsters(self):
        return self.monsters

    def __cmp__(self, other):
        return cmp(self.get_title(), other.get_title())

    def load(self):
        root = self.doc.getroot()

        # check it's the right sort of element
        if root.tag != "monstergroup":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))
        
        # handle all the children of the monster group
        for child in list(root):
        
           tag = child.tag
           if tag == "monstergroupinfo":
               if self.info is not None:
                   raise Exception("Only one monstergroupinfo per file.")
               else:
                   self.info = MonsterGroupInfo(self.fname)
                   self.info.load(child)

           elif tag == "monster":
               monster = Monster(self.fname)
               monster.load(child)
               self.monsters.append(monster)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    def get_rank(self):
        return self.info.rank
    
        
class MonsterClass:
    NONE = "None"

    # melee monsters
    AMBUSH = "Ambush"
    SURPRISE = "Surprise"
    INITIATIVE = "Initiative"
    TALK = "Talk"
    #ACT = "Act"
    #RUN = "Run"
    #FIGHT_RANGED = "Fight-Ranged"
    FIGHT_REACH = "Fight-Reach"
    #FIGHT = "Fight"
    START = "Start"
    FAST = "Fast"
    MEDIUM = "Medium"
    SLOW = "Slow"
    RESOLUTION = "Resolution"
    REACTION = "Reaction"
    NON_COMBAT = "Non-Combat"

    # misc monsters
    LORE = "Lore"

    @classmethod
    def to_string(cls, monster_class):
        if monster_class is None:
            return MonsterClass.NONE
        return cls._names[stage]

    @staticmethod
    def get_symbol(monster_class):
        
        if monster_class is not None:
            monster_class = monster_class.strip()

        if monster_class == "none":            
            symbol_str = "NONE!"
            raise Exception("X")
        elif monster_class == MonsterClass.AMBUSH:
            monster_cls = "<ambushsymbol/>"
        elif monster_class == MonsterClass.SURPRISE:
            symbol_str = "<surprisesymbol/>"
        elif monster_class == MonsterClass.INITIATIVE:
            symbol_str = "<initiativesymbol/>"
        elif monster_class == MonsterClass.TALK:
            symbol_str = "<talksymbol/>"
        elif monster_class == MonsterClass.START:
           symbol_str = "<startsymbol/>"
        elif monster_class == MonsterClass.FAST:
           symbol_str = "<fastsymbol/>"
        elif monster_class == MonsterClass.MEDIUM:
           symbol_str = "<mediumsymbol/>"
        elif monster_class == MonsterClass.SLOW:
           symbol_str = "<slowsymbol/>"
            
        #elif monster_class == MonsterClass.ACT:
        #    symbol_str = "<actsymbol/>"
        #elif monster_class == MonsterClass.RUN:
        #    symbol_str = "<runsymbol/>"
        #elif monster_class == MonsterClass.FIGHT_RANGED:
        #    symbol_str = "<fightrangedsymbol/>"
        elif monster_class == MonsterClass.FIGHT_REACH:
            symbol_str = "<fightreachsymbol/>"
        #elif monster_class == MonsterClass.FIGHT:
        #    symbol_str = "<fightsymbol/>"
        elif monster_class == MonsterClass.RESOLUTION:
            symbol_str = "<resolutionsymbol/>"
        elif monster_class == MonsterClass.REACTION:
            symbol_str = "<reactionsymbol/>"
        elif monster_class == MonsterClass.NON_COMBAT:
            symbol_str = "<noncombatsymbol/>"
        else:
            symbol_str = "UNKNOWN! %s" % monster_class
            raise Exception("X")
        return symbol_str

    
    @staticmethod
    def load(monster_class):
        monster_cls = MonsterClass.NONE

        if monster_class is not None:
            monster_class = monster_class.lower().strip()

        if monster_class == "none":
            monster_cls = MonsterClass.NONE
        elif monster_class == "surprise":
            monster_cls = MonsterClass.SURPRISE
        elif monster_class == "initiative":
            monster_cls = MonsterClass.INITIATIVE
        elif monster_class == "talk":
            monster_cls = MonsterClass.TALK
        # elif monster_class == "act":
        #     monster_cls = MonsterClass.ACT
        # elif monster_class == "run":
        #     monster_cls = MonsterClass.RUN
        # elif monster_class == "fight":
        #     monster_cls = MonsterClass.FIGHT
        # elif monster_class == "fight-ranged":
        #     monster_cls = MonsterClass.FIGHT_RANGED
        elif monster_class == "fight-reach":
            monster_cls = MonsterClass.FIGHT_REACH
        elif monster_class == "resolution":
            monster_cls = MonsterClass.RESOLUTION
        elif monster_class == "reaction":
            monster_cls = MonsterClass.REACTION
        elif monster_class == "start":
            monster_cls = MonsterClass.START
        elif monster_class == "fast":
            monster_cls = MonsterClass.FAST
        elif monster_class == "medium":
            monster_cls = MonsterClass.MEDIUM
        elif monster_class == "slow":
            monster_cls = MonsterClass.SLOW
        elif monster_class == "non-combat":
            monster_cls = MonsterClass.NON_COMBAT
        else:
            monster_cls = MonsterClass.NONE
        return monster_cls


class Monster:
    """
    An monster.

    """
    # set of all monster ids we've seen
    # there should be no duplicates!
    _ids = {}

    def __init__(self, fname):
        self.fname = fname
        self.title = None
        self.monster_id = None
        self.description = None
        self.tags = [] 
        self.aspects = [] 
        self.monster_class = MonsterClass.NONE
        self.ac = 7 # FIXME
        self.health = 8 # FIXME
        self.stamina = 9 # FIXME
        self.abilities = ["Frog II", "Dog O"]
        return

    def get_monster_class_symbol(self):
        return MonsterClass.get_symbol(self.monster_class)

    def get_description(self):
        return self.description

    def get_title(self):
        return self.title

    def get_ac(self):
        return self.ac

    def get_abilities_str(self):
        return ", ".join(self.abilities)

    def get_stamina(self):
        return self.stamina

    def get_health(self):
        return self.health

    #def get_monster_class(self):
    #    return self.monster_class


    def get_id(self):
        return self.monster_id

    def get_monster_class(self):
        if self.monster_class is None:
            return "missing"

        return self.monster_class.lower()            

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
        print "TAGS STR" + "" if len(self.tags) == 0 else ", ".join(self.tags)
        return "" if len(self.tags) == 0 else ", ".join(self.tags)

    def get_aspects_str(self):
        return ", ".join(self.aspects)

    def load(self, monster_element):
        # check it's the right sort of element
        if monster_element.tag != "monster":
            raise Exception("UNKNOWN (%s) %s\n" % (monster_element.tag,
                                                   str(monster_element)))
        self._load(monster_element)
        return


    def _get_location(self, lxml_element):
        return "%s:%s" % (self.fname, lxml_element.sourceline)


    def _load(self, monster_element):
        print "---------------------____"
        
        # handle all the children
        for child in list(monster_element):              
           tag = child.tag
           print tag
           if tag == "monstertitle":
               if self.title is not None:
                   raise Exception("Only one monstertitle per monster. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:                   
                   self.title = child.text

           elif tag == "monsterid":
               if self.monster_id is not None:
                   raise Exception("Only one monsterid per monster. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # check for duplicates!
                   monster_id = child.text
                   monster_location = self._get_location(child)
                   if monster_id in self._ids:
                       raise Exception("Monster id: %s appears in two places %s and %s"
                                       % (monster_id,
                                          monster_location,
                                          self._ids[monster_id]))
                   else:
                        self._ids[monster_id] = monster_location

                   # save the id!
                   self.monster_id = monster_id

           elif tag == "monstertag":
               print "XXX"
               print child.text
               self.tags.append(child.text)

           elif tag == "monsteraspect":
               self.aspects.append(child.text)

           elif tag == "monsterclass":
               self.monster_class = MonsterClass.load(child.text)
               if self.monster_class == MonsterClass.NONE:
                   raise Exception("Unknown monster class: (%s) %s in %s\n" %
                                   (child.tag, child.text, self.fname))

           elif tag == "monsterdescription":
               if self.description is not None:
                   raise Exception("Only one monsterdescription per monster. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   #self.description = get_text(child)                   
                   #self.description = node_to_string(child)                   
                   self.description = children_to_string(child)                   

           elif tag is COMMENT:
               # ignore comments!
               pass

           else:
               raise Exception("UNKNOWN (%s) in file %s\n" % 
                               (child.tag, self.fname))
        return

    # def load_monster_levels(self, monster_levels):
    #     # handle all the children
    #     for child in list(monster_levels):
        
    #        tag = child.tag
    #        if tag == "monsterlevel":
    #            level = MonsterLevel.load_monster_level(
    #                monster = self, 
    #                monster_level_element = child)

    #            # check we don't already have an monster level with the same level number!
    #            for other_level in self.levels:
    #                if other_level.get_level_number() == level.get_level_number():
    #                    raise Exception(
    #                        "Received two monster level definitions for monster: %s"
    #                        % level.get_title())
    #            self.levels.append(level)

    #        elif tag is COMMENT:
    #            # ignore comments!
    #            pass
    #        else:
    #            raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

    #     # now sort the levels.
    #     def get_level_key(level):
    #         return level.level_number
    #     self.levels.sort(key = get_level_key)
    #     return


if __name__ == "__main__":

    monster_groups = MonsterGroups()
    monster_groups_dir = join(root_dir, "monsters")
    monster_groups.load(monster_groups_dir, fail_fast = True)
    
    # build_dir = join(root_dir, "build")
    # #monster_groups.draw_all_skill_trees(build_dir)
    # #monster_groups.draw_skill_tree(build_dir)
    # #monster_groups.draw_skill_tree2(build_dir)

    # for monster_group in monster_groups:
    #     print(monster_group.get_title())

    #     for monster in monster_group:

    #         if "eering" not in monster.get_title():
    #             continue
            
    #         print("\t%s" % monster.get_title())
    #         print("\t\t\tMonster Class: %s" % monster.get_monster_class())
    #         print("\t\t\tMonster Desc: %s" % monster.description)
    #         #print("\t\t\tMonster Class: %s" % monster.get_monster_class())
    #         #print("\t\t\t\t: %s" % monster.get_monster_class())
            
    #         for monster_level in monster.get_levels():
    #             print("\t\t\t\t%s" % monster_level.get_title())
    #             print("\t\t\t\t%s" % monster_level.check)
    #             print("\t\t\t\t%s" % monster_level.description)
    #         #    #print("\t\t\tLore: %s" % monster_level.get_default_lore())



