import os
from os.path import split

from utils import parse_xml, validate_xml, node_to_string, COMMENT

    
class MonsterPack:
    """
    This is a wrapper around the monster class.  It's here to 
    allow customization.

    """
    def __init__(self):
        # Same as the monster id.
        self._id = None
        self.count = None
        # Optional name overload for the encounter descriptions
        self.name = None

        # For some things it's easier to 
        self.monster_groups = None
        self.monster = None


    def set_monster_groups(self, monster_groups):
        self.monster_groups = monster_groups
        self.monster = monster_groups.get_monster_by_id(self._id)
        

    def load(self, monster_element):
        # handle all the children of the monster pack
        for child in list(monster_element):
           tag = child.tag
           if tag == "id":
               if self._id is not None:
                   raise Exception("Only one id per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self._id = child.text


           elif tag == "count":
               if self.count is not None:
                   raise Exception("Only one count per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.count = int(child.text)

           elif tag == "name":
               if self.name is not None:
                   raise Exception("Only one name per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.name = child.text

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

    def get_name(self):
        return self.name if self.name else self.monster.title

    def __getattr__(self, attr_name):
        return getattr(self.monster, attr_name)
            
           
class Encounter:

    def __init__(self):
        self._id = None
        self.name = None
        self.precis = None
        self.details = None
        self.motivation = None
        self.timers = None
        self.threats = None
        self.treats = None
        self.progression = None
        self.difficulty = None
        self.strategy = None
        self.outs = None
        self.monsters = []

        # mp = MonsterPack()
        # mp.monster_id = 'green_skins.goblin'
        # mp.count = 3
        # self.monsters.append(mp)

        self.fname = None
        self.doc = None 


    def load(self, fname):
        f = open(fname)
        self.fname = fname 
        self.doc = parse_xml(fname)
        if self.doc is None:
            # failed to parse
            raise Exception(f"Failed to parse {fname}!!")

        # err_msg = validate_xml(self.doc)
        # if not err_msg is None:
        #     raise Exception(f"Fatal: xml errors are fatal! {err_msg}")
        
        root = self.doc.getroot()

        # check it's the right sort of element
        if root.tag != "encounter":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))

        
        # handle all the children of the monster group
        for child in list(root):
           tag = child.tag
           if tag == "encounterid":
               if self._id is not None:
                   raise Exception("Only one encounterid per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self._id = child.text


           elif tag == "name":
               if self.name is not None:
                   raise Exception("Only one name per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.name = child.text

           elif tag == "motivation":
               if self.motivation is not None:
                   raise Exception("Only one motivation per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.motivation = child.text

           elif tag == "timers":
               if self.timers is not None:
                   raise Exception("Only one timers per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.timers = child.text

           elif tag == "treats":
               if self.treats is not None:
                   raise Exception("Only one treats per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.treats = child.text


           elif tag == "threats":
               if self.threats is not None:
                   raise Exception("Only one threats per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.threats = child.text

           elif tag == "details":
               if self.details is not None:
                   raise Exception("Only one details per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.details = child.text
                   #self.details = node_to_string(child)

           elif tag == "precis":
               if self.precis is not None:
                   raise Exception("Only one precis per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.precis = child.text

           elif tag == "progression":
               if self.progression is not None:
                   raise Exception("Only one progression per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.progression = child.text

           elif tag == "difficulty":
               if self.difficulty is not None:
                   raise Exception("Only one difficulty per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.difficulty = child.text

           elif tag == "strategy":
               if self.strategy is not None:
                   raise Exception("Only one strategy per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.strategy = child.text

           elif tag == "outs":
               if self.outs is not None:
                   raise Exception("Only one outs per encounter. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.outs = child.text

           elif tag == "monster":

               monster = MonsterPack()
               monster.load(child)
               self.monsters.append(monster)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

        #assert self.info.title
        #import sys; sys.exit()
        return
        

    def get_monsters(self, monster_groups=None):
        for monster_pack in self.monsters:
            monster_pack.set_monster_groups(monster_groups)
        return self.monsters

        
class Encounters:

    def __init__(self):
        self.encounters = {}


    def load(self, root_dir):
        encounter_fnames = []
        for root, dirs, files in os.walk(".", topdown=False):
            #print(f"root {root}")
            if split(root)[-1] == "encounters":
                for name in files:
                    if name.endswith(".xml"):                    
                        encounter_fnames.append(os.path.join(root, name))

        for encounter_fname in encounter_fnames:
            encounter = Encounter()
            encounter.load(fname=encounter_fname)
            self.encounters[encounter._id] = encounter

    def get(self, encounter_id):
        return self.encounters[encounter_id]
        
