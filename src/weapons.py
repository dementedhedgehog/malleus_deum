#!/usr/bin/env python
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
from os import listdir
from collections import defaultdict

from utils import (
    parse_xml,
    validate_xml,
    node_to_string,
    COMMENT,
    contents_to_string,
    contents_to_comma_separated_list)
        
src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))


class Weapon:

    def __init__(self, fname):
        self.fname = fname
        
        self.name = None
        self.damage = None
        self.price = None
        self.tags = None
        self.missile_range = None
        # Weapons save
        self.save = None

    def __str__(self):
        return (f"{self.name} - dmg:{self.damage}, price:{self.price}, " +
                f"save:{self.save}, tags:{self.tags}" +
                "" if self.missile_range is None else f" range:{self.missile_range}")

    def load(self, node):
        # check it's the right sort of element
        if node.tag != "weapon":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))
        
        # handle all the children of the ability group
        for child in list(node):
        
           tag = child.tag
           if tag == "name":
               if self.name is not None:
                  raise Exception("Only one name per weapon.")
               else:
                   self.name = child.text.strip()
                   
           elif tag == "damage":
               if self.damage is not None:
                  raise Exception("Only one damage per weapon.")
               else:
                   self.damage = child.text.strip()
                   
           elif tag == "price":
               if self.price is not None:
                  raise Exception("Only one price per weapon.")
               else:
                   self.price = child.text.strip()
                   
           elif tag == "save":
               if self.save is not None:
                  raise Exception("Only one save per weapon.")
               else:
                   #self.save = child.text.strip()
                   self.save = contents_to_string(child)
                   # self.save = node_to_string(child)
                   
           elif tag == "range":
               if self.missile_range is not None:
                  raise Exception("Only one range per weapon.")
               else:
                   #self.missile_range = child.text.strip() 
                   self.missile_range = contents_to_string(child) # .text.strip() 

           elif tag == "tags":
               if self.tags is not None:
                  raise Exception("Only one tags per weapon.")
               else:
                   #print(contents_to_string(child))
                   self.tags = contents_to_comma_separated_list(child)
                   #self.tags = child.tag[1:-2]

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return
        
        

class Weapons:
    """
    A list of all weapons

    """
    def __init__(self, fname):
        self.fname = fname
        self.weapons = []
        self.doc = parse_xml(fname) 
        result = validate_xml(self.doc)
        if result is not None:
            raise Exception(result)
        return

    def __iter__(self):
        return iter(self.weapons)

    def load(self, node = None):

        if node is None:
            root = self.doc.getroot()
        else:
            root = node

        # check it's the right sort of element
        if root.tag != "weapons":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))
        
        # handle all the children of the ability group
        for child in list(root):
        
           tag = child.tag
           if tag == "weapon":
               #if self.info is not None:
               #    raise Exception("Only one abilitygroupinfo per file.")
               #else:
               weapon = Weapon(self.fname)
               weapon.load(child)
               self.weapons.append(weapon)

           # elif tag == "ability":
           #     ability = Ability(self.fname)
           #     ability.load(child)
           #     self.abilities.append(ability)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return


    
if __name__ == "__main__":

    weapons_xml = join(root_dir, "items", "melee_weapons.xml")
    #weapons_xml = join(root_dir, "items", "weapons.xml")
    weapons = Weapons(fname=weapons_xml)
    weapons.load()
    for weapon in weapons:
        print(weapon)
