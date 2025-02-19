#!/usr/bin/env python
from os.path import join
from os import listdir, walk
import os

from utils import (
    parse_xml, validate_xml, children_to_string, contents_to_string,
    COMMENT, convert_str_to_int, convert_to_roman_numerals,
    root_dir
)

from monsters import MonsterGroups


class NPC:
    """
    NPC info shared between NPC and SimpleNPC.

    """

    def __init__(self, npc_group=None):

        # These values shadow those in the monster class
        # we use these to enable people to override the
        # default monster values
        self.ac = None
        self.name = None
        self.move = None
        self.magic_pool = None
        self.initiative_bonus = None
        self.resolve = None
        self.monster_id = None
        self.monster = None
        self.strength = None
        self.endurance = None
        self.agility = None
        self.speed = None
        self.luck = None
        self.willpower = None
        self.perception = None
        self.name = None
        self.health = None
        self.stamina = None
        self.tags_str = None
        
        if npc_group is not None:
            self.health = npc_group.get_health()
            self.stamina = npc_group.get_stamina()
            self.tags_str = npc_group.get_keywords_str()

        self.ability_level_ids = []
        self.npc_group = npc_group        
        return
    
    def is_npc_group(self):
        return False

    def get_name(self):
        return self.name
    
    def get_monster_id(self):
        return self.monster_id

    def get_initiative_bonus(self):
        return self.initiative_bonus

    def get_keywords_str(self):
        return self.monster.get_keywords_str()
    
    def get_title(self):
        return self.title

    def get_stamina(self):
        result = None
        if self.stamina is not None:
            result = self.stamina
        elif self.monster is not None:
            result = self.monster.stamina
        return result    
        #return self.stamina
    
    def get_health(self):
        result = None
        if self.health is not None:
            result = self.health
        elif self.health is not None:
            result = self.monster.health
        return result    
        #return self.health

    def get_aspects_str(self):
        return self.monster.get_aspects_str()    

    def get_description(self):
        return self.monster.get_description()
    
    def get_ability_level_ids(self):
        result = self.ability_level_ids            
        if self.monster is not None:
            result += self.monster.get_ability_level_ids()
        return result
    
    def get_magic_pool(self):
        result = None
        if self.magic_pool is not None:
            result = self.magic_pool
        elif self.monster is not None:
            result = self.monster.magic_pool
        return result
    
    def get_resolve_pool(self):
        result = None
        if self.resolve is not None:
            result = self.resolve
        elif self.monster is not None:
            result = self.monster.resolve
        return result
    
    def get_ac(self):
        result = None
        if self.ac is not None:
            result = self.ac
        elif self.monster is not None:
            result = self.monster.ac
        return result

    def get_move(self):
        result = None
        if self.move is not None:
            result = self.move
        elif self.monster is not None:
            result = self.monster.move
        return result

    def get_strength(self):
        result = None
        if self.strength is not None:
            result = self.strength
        elif self.monster is not None:
            result = self.monster.strength
        return result

    def get_endurance(self):
        result = None
        if self.endurance is not None:
            result = self.endurance
        elif self.monster is not None:
            result = self.monster.endurance
        return result

    def get_agility(self):
        result = None
        if self.agility is not None:
            result = self.agility
        elif self.monster is not None:
            result = self.monster.agility
        return result

    def get_speed(self):
        result = None
        if self.speed is not None:
            result = self.speed
        elif self.monster is not None:
            result = self.monster.speed
        return result


    def get_luck(self):
        result = None
        if self.luck is not None:
            result = self.luck
        elif self.monster is not None:
            result = self.monster.luck
        return result


    def get_willpower(self):
        result = None
        if self.willpower is not None:
            result = self.willpower
        elif self.monster is not None:
            result = self.monster.willpower
        return result


    def get_perception(self):
        result = None
        if self.perception is not None:
            result = self.perception
        elif self.monster is not None:
            result = self.monster.perception
        return result

    
    def parse(self, node, monster_groups):        
         for child in list(node):
            tag = child.tag

            if tag == "monsterid":
                self.monster_id = child.text
                self.monster = monster_groups.get_monster_by_id(self.monster_id)

            elif tag == "name":
                self.name = child.text

            elif tag == "resolve":
                self.health = child.text

            elif tag == "magic_pool":
                self.health = child.text
                
            elif tag == "health":
                self.health = child.text

            elif tag == "stamina":
                self.stamina = child.text

            else:
                raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
         return


class NPCGroup:
    """
    A group of npcs of the *same* monster type..

    """
    def __init__(self, monster_groups):
        self.npcs = []
        self.monster_id = None
        self.monster_groups = monster_groups
        return

    def get_monster_id(self):
        return self.monster_id

    def get_title(self):
        return self.monster.get_title()

    def get_keywords_str(self):
        return self.monster.get_keywords_str()

    def get_initiative_bonus(self):
        return self.monster.get_initiative_bonus()    
        
    def get_strength(self):
        return self.monster.strength

    def get_endurance(self):
        return self.monster.endurance

    def get_agility(self):
        return self.monster.agility

    def get_speed(self):
        return self.monster.speed

    def get_luck(self):
        return self.monster.luck

    def get_willpower(self):
        return self.monster.willpower

    def get_perception(self):        
        return self.monster.perception

    def get_ability_level_ids(self):
        return self.monster.get_ability_level_ids()

    def get_ac(self):
        return self.monster.ac

    def get_stamina(self):
        return self.monster.get_stamina()

    def get_health(self):
        return self.monster.get_health()
    
    def get_resolve_pool(self):
        return self.monster.resolve

    def get_magic_pool(self):
        return self.monster.magic_pool

    def get_aspects_str(self):
        return self.monster.get_aspects_str()    
    
    def get_move(self):
        return self.monster.move
    
    def __iter__(self):
        return iter(self.npcs)


    def parse(self, npcgroup):
        for child in list(npcgroup):
           tag = child.tag

           if tag == "monsterid":
               self.monster_id = child.text
               self.monster = self.monster_groups.get_monster_by_id(self.monster_id)
               self.monster = self.monster_groups.get_monster_by_id(self.monster_id)

           elif tag == "npc":
               npc = NPC(npc_group=self)
               npc.parse(child, monster_groups=self.monster_groups)
               self.npcs.append(npc)

           elif tag is COMMENT:
               # ignore comments!
               pass
           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

        for npc in self.npcs:
            npc.monster = self.monster
        return

    def is_npc_group(self):
        return True


    
class NPCGang:
    """
    A list of npc_likes (i.e. a list of npc or npc_groups).

    """

    # map of npc_id -> npcs.
    npc_like_lookup = {}

    def __init__(self, monster_groups):
        self.npc_likes = []
        self.npcs_id = None
        self.monster_groups = monster_groups
        return

    def __iter__(self):
        return iter(self.npc_likes)

    def __getitem__(self, key):
        return self.npc_likes[key]   

    def get_id(self):
        return self.npcs_id

    def parse(self, npcs_node):
        for child in list(npcs_node):
           tag = child.tag

           if tag == "npcsid":
               self.npcs_id = child.text

           elif tag == "npc":
               npc = NPC()
               npc.parse(child, monster_groups=self.monster_groups)
               self.npc_likes.append(npc)

           elif tag == "npcgroup":
               npc_group = NPCGroup(monster_groups=self.monster_groups)
               npc_group.parse(child)
               self.npc_likes.append(npc_group)

           elif tag is COMMENT:
               # ignore comments!
               pass
           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return

    @classmethod
    def load(cls, npcs_dir, monster_groups, fail_fast):
        result = True

        for root, dirs, files in walk(npcs_dir, topdown=False):
            for name in files:            
                if not name.endswith(".xml"):
                    continue

                if name.startswith(".#"):
                    continue
            
                xml_fname = join(root, name)                
                doc = parse_xml(xml_fname)
                root = doc.getroot()
                if root.tag == "npcs":
                    npcs = NPCs(monster_groups=monster_groups)
                    npcs.parse(root)
                    if not npcs.validate():
                        result = False
                        if fail_fast:
                            raise Exception("Errors in %s" % xml_fname)                
                    else:
                        cls.npc_like_lookup[npcs.npcs_id] = npcs
        return result
    

    def validate(self):
        # FIXME: placeholder
        return True

    def is_npc_group(self):
        return True


class NPCGangs:
    """
    A lookup table of npc_gangs.

    """

    def __init__(self):
        # map of npc_id -> npcs.
        self.npc_gang_lookup = {}        
        return

    def __iter__(self):
        return iter(self.npc_gang_lookup.items())

    def __getitem__(self, key):
        return self.npc_gang_lookup[key]   
    

    def load(self, npcs_dir, monster_groups, fail_fast):
        result = True
        
        # load all the monster groups
        for root, dirs, files in os.walk(npcs_dir, topdown=False):

            for name in files:
                if not name.endswith(".xml"):
                    continue

                if name.startswith(".#"):
                    continue

                xml_fname = os.path.join(root, name)

                doc = parse_xml(xml_fname)
                doc_root = doc.getroot()
                if doc_root.tag == "npcs":
                    npcs = NPCGang(monster_groups=monster_groups)
                    npcs.parse(doc_root)
                    if not npcs.validate():
                        result = False
                        if fail_fast:
                            raise Exception("Errors in %s" % xml_fname)                
                    else:
                        self.npc_gang_lookup[npcs.npcs_id] = npcs
        return result
    

    def validate(self):
        # FIXME: placeholder
        return True


if __name__ == "__main__":
    fail_fast = True

    monsters_dir = join(root_dir, "monsters")
    monster_groups = MonsterGroups()
    monster_groups.load(monsters_dir, fail_fast=fail_fast)
    
    npcs_dir = join(root_dir, "encounters")
    npc_gangs = NPCGangs()
    npc_gangs.load(npcs_dir=npcs_dir,
                   monster_groups=monster_groups,
                   fail_fast=fail_fast)
    
    for npc_like in npc_gangs:
        print(npc_like)
    print()
