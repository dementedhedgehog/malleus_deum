#!/usr/bin/env python
from os.path import join
from os import listdir
from os.path import abspath, dirname

from utils import (
    parse_xml,
    #validate_xml,
    children_to_string, contents_to_string, node_to_string,
    #COMMENT,
    is_comment,
    convert_str_to_int,
)
from abilities import AbilityRef

        

class MonsterGroups:
    """
    A list of all enabled skills.

    """
    def __init__(self):
        self.monster_groups = []
        self.monster_lookup = {}
        return
    
    def __len__(self):
        count = 0
        for group in self.monster_groups:
            count += len(group)
        return count
    
    def load(self, monsters_dir, fail_fast):
        result = True
        # load all the monster groups
        for xml_fname in listdir(monsters_dir):
            if not xml_fname.endswith(".xml"):
                continue

            if xml_fname.startswith(".#"):
                continue

            xml_fname = join(monsters_dir, xml_fname)
            monster_group = MonsterGroup(xml_fname)
            # if not monster_group.validate():
            #     result = False
            #     if fail_fast:
            #         raise Exception("Errors in %s" % xml_fname)
                
            monster_group.load()

            self.monster_groups.append(monster_group)

            # populate the monster_id -> monster lookup table
            for monster in monster_group.get_monsters():
                self.monster_lookup[monster.get_id()] = monster

        # sort the groups
        self.monster_groups.sort()
        return result    

    def get_monster_by_id(self, monster_id):
        return self.monster_lookup[monster_id]

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
                   
           # elif tag == "monstergroupfamily":
           #      self.family = child.text
           #      assert self.family in ("Mundane", "Combat", "Magic")
                
           elif tag == "monstergroupdescription":
               if self.description is not None:
                   raise Exception("Only one monstergroupdescription per file.")
               else:                   
                   self.description = contents_to_string(child)

           #elif tag is COMMENT:
           elif is_comment(child): # tag is COMMENT:
               pass # ignore comments!

           else:
               #
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return



class MonsterGroup:

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
        
    # def validate(self):
    #     valid = True
    #     error_log = validate_xml(self.doc)
    #     if error_log is not None:
    #         valid = False
    #         print("Errors (XSD)!")
    #         print("\t%s" % error_log)
    #     return valid

    # def get_family(self):
    #     return self.info.family

    def __len__(self):
        return len(self.monsters)
    
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

    def __lt__(self, other):
        return self.get_title() < other.get_title()

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
                monster = Monster(fname=self.fname)
                monster.load(child)
                self.monsters.append(monster)

            #elif tag is COMMENT:
            elif is_comment(child):
                pass # ignore comments!

            else:
                raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))

        assert self.info.title
        return

    def get_rank(self):
        return self.info.rank


class MonsterVariant:

    def __init__(self, monster):
        self.monster = monster
        self.title = None
        self.variant_id = None
        self.ability_refs = []

    def parse(self, variant_element):
        for child in list(variant_element):              
           tag = child.tag
           if tag == "varianttitle":
               if self.title is not None:
                   raise Exception(
                       "Only one varianttitle per variant. (%s) %s\n" %
                       (child.tag, str(child)))
               else:                   
                   self.title = child.text
           elif tag == "variantid":
               pass
               # if self.variant_id is not None:
               #     raise Exception("Only one variantid per variant. (%s) %s\n" %
               #                     (child.tag, str(child)))
               # else:
               #     # check for duplicates!
               #     variant_id = child.text
               #     if monster_id in self._ids:
               #         variant_location = "%s:%s" % (self.fname, lxml_element.sourceline)
               #         raise Exception("Monster id: %s appears in two places %s and %s"
               #                         % (variant_id,
               #                            variant_location,
               #                            self.monster._ids[variant_id]))
               #     else:
               #          self.monster._ids[variant_id] = self

               #     # save the id!
               #     self.monster_id = monster_id

           elif tag == "abilityref":
               ref = AbilityRef()
               ref.parse(child)
               self.ability_refs.append(ref)

           elif is_comment(child):               
               pass # ignore comments!
           
           else:
               raise Exception("UNKNOWN (%s) in file %s\n" % 
                               (child.tag, self.monster.fname))
        return

               
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
        self.keywords = [] 
        self.aspects = []
        # ability_id -> ability_ref
        self.ability_refs = {}
        self.move = None
        self.role = None

        self.variants = []
        
        # defence
        # self.armour = None
        # self.dodge = None
        # self.parry = None
        # self.block = None
        #self.ability_rank_ids = []
        #self.ability_refs = []
        
        self.initiative = None
        self.health = 0
        self.stamina = 0
        self.mettle_pool = None
        self.magic_pool = None
        self.luck_pool = None
        #self.strength = None
        #self.endurance = None
        #self.agility = None
        #self.speed = None
        #self.perception = None
        #self.will = None

        self.img = None
        return
    
    def get_passive_check_desc(self, ability_rank, check):
        target_dc = 10 + ability_rank.rank_number

        # For passive dcs the monster is the opponent!
        desc = "Missing description!!"
        match check.dc:
            case "opponents-attack":
                desc = f"Attack vs {target_dc}"
            case "opponents-defend":      
                desc = f"Defend vs {target_dc}"
            case "opponents-strength":
                desc = f"Strength vs {target_dc}"
            case "opponents-agility":
                desc = f"Agility vs {target_dc}"
            case "opponents-speed":
                desc = f"Speed vs {target_dc}"
            case "opponents-perception":
                desc = f"Perception vs {target_dc}"
            case "opponents-will":
                desc = f"Will vs {target_dc}"
            case "opponents-endurance":
                desc = f"Endurance vs {target_dc}"
            case "gm-fiat":
                desc = "GM Fiat DC"
            case "opponents-negotiate-or-11":
                desc = "Negotiate or 11"
            case "opponents-etiquette-or-11":
                desc = "Etiquette or 11"
            case "aspect-dc":
                desc = "Aspect DC"
            # case "strength":
            #     desc = ""
            # case "agility":
            #     desc = ""
            # case "speed":
            #     desc = ""
            # case "endurance":
            #     desc = ""
            # case "will":
            #     desc = ""
            # case "perception":
            #     desc = ""
            case "dc9-plus-rank":
                desc = "DC 9+Rank"
            case "dc11-plus-rank":
                desc = "DC 11+Rank"
            case "dc13-plus-rank":
                desc = "DC 13+Rank"
            case "dc15-plus-rank":
                desc = "DC 15+Rank"
            case "dc3":
                target_dc = max(3 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc5":
                target_dc = max(5 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc7":
                target_dc = max(7 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc9":
                target_dc = max(9 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc11":
                target_dc = max(11 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc13":
                target_dc = max(13 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc15":
                target_dc = max(15 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc17":
                target_dc = max(17 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc19":
                target_dc = max(19 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc21":
                target_dc = max(21 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc23":
                target_dc = max(23 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc25":
                target_dc = max(25 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
            case "dc27":
                target_dc = max(27 - ability_rank.rank_number, 2)
                desc = f"Flat {target_dc}"
                
        return desc
        
    

    
    # def validate(self):
    #     assert self.magic_pool is not None
    #     return

    def get_strength(self):
        #return self.strength
        return self._get_ability_ref("strength")


    def get_endurance(self):
        #return self.endurance
        return self._get_ability_ref("endurance")

    def get_agility(self):
        #return self.agility
        return self._get_ability_ref("endurance")
 
    def get_perception(self):
        #return self.perception
        return self._get_ability_ref("endurance")

    def get_will(self):
        #return self.will
        return self._get_ability_ref("endurance")

    def get_speed(self):
        #return self.speed
        return self._get_ability_ref("endurance")

    def get_luck(self):
        return self.luck_pool

    def get_mettle_pool(self):
        return self.mettle_pool

    def get_move(self):
        return self.move

    def get_initiative(self):
        return self.initiative    

    def get_magic_pool(self):
        return self.magic_pool

    def get_description(self):
        return self.description

    def get_ability_refs(self):
        return self.ability_refs.values()

    def _get_ability_ref(self, _id):
        return self.ability_refs.get(_id)

    def get_title(self):
        return self.title
    
    def get_armour(self):
        return self._get_ability_ref("armour")

    def get_dodge(self):
        return self._get_ability_ref("dodge")

    def get_block(self):
        return self._get_ability_ref("block")

    def get_parry(self):
        return self._get_ability_ref("parry")

    def get_defences(self):
        """Return a comma separated list of defences."""
        defences = []
        if self.armour:
            defences.append(f"Armour:{self.get_armour()}")
        if self.parry:
            defences.append(f"Parry:{self.get_parry()}")
        if self.block:
            defences.append(f"Block:{self.get_block()}")
        if self.dodge:
            defences.append(f"Dodge:{self.get_dodge()}")
        return ", ".join(defences)
            

    def get_stamina(self):
        return self.stamina

    def get_health(self):
        return self.health

    def get_id(self):
        return self.monster_id

    # def get_monster_class(self):
    #     if self.monster_class is None:
    #         return "missing"
    #     return self.monster_class.lower()

    def has_prerequisites(self):
        has_prereqs = False
        for rank in self.ranks:
            if rank.has_prerequisites():
                has_prereqs = True
                break
        return has_prereqs

    def has_keywords(self):
        return len(self.keywords) > 0

    def get_keywords_str(self):
        return "" if len(self.keywords) == 0 else ", ".join(self.keywords)

    def get_abilities_str(self):
        #return "X" if len(self.abilities) == 0 else ", ".join(self.abilities)
        return ", ".join(self.abilities)

    def get_aspects_str(self):
        return ", ".join(self.aspects)

    def load(self, monster_element):
        # check it's the right sort of element
        if monster_element.tag != "monster":
            raise Exception("UNKNOWN (%s) %s\n" % (monster_element.tag,
                                                   str(monster_element)))
        self._load(monster_element)
        return

    def parse_monster_role(self, monster_roles_node):
        for child in list(monster_roles_node):
            #if child.tag is not COMMENT:
            if not is_comment(child): #  is not COMMENT:
                tag = child.tag[1:-2]
                self.monster_role = child.tag
        return    

    def _get_location(self, lxml_element):
        return "%s:%s" % (self.fname, lxml_element.sourceline)
    
    def _load(self, monster_element):
        # handle all the children
        for child in list(monster_element):              
           tag = child.tag
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

           elif tag == "img":
               if self.img is not None:
                   raise Exception(
                       "Only one monsterimg per monster. You can add more in the description or "
                       "in the monster group description.  (%s) %s\n" %
                       (child.tag, str(child)))
               else:
                   self.img = node_to_string(child)

           elif tag == "monsterkeywords":
               for tag in child:
                   self.keywords.append(tag.tag)

           elif tag == "monsterabilities":               
               #for tag in child:
               self.abilities = child.text

           elif tag == "monstermove":
               self.move = convert_str_to_int(child.text)

           elif tag == "monsterhealth":
               self.health = convert_str_to_int(child.text)

           elif tag == "monsterstamina":
               self.stamina = convert_str_to_int(child.text)

           elif tag == "monstermettle":
               self.mettle_pool = child.text
               
           elif tag == "monstermagic":
               self.magic_pool = child.text

           elif tag == "monsteraspect":
               self.aspects.append(child.text)

           elif tag == "monsterinitiative":
               self.initiative = convert_str_to_int(child.text)

           elif tag == "monsterrole":
               self.parse_monster_role(child)

           # elif tag == "armour":
           #     self.armour = child.text

           # elif tag == "dodge":
           #     self.dodge = child.text

           # elif tag == "parry":
           #     self.parry = child.text

           # elif tag == "block":
           #     self.block = child.text

           # elif tag == "strength":
           #     if self.strength is not None:
           #         raise Exception("Only one strength per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.strength = convert_str_to_int(child.text)

           # elif tag == "endurance":
           #     if self.endurance is not None:
           #         raise Exception("Only one endurance per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.endurance = convert_str_to_int(child.text)


           # elif tag == "agility":
           #     if self.agility is not None:
           #         raise Exception("Only one agility per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.agility = convert_str_to_int(child.text)


           # elif tag == "speed":
           #     if self.speed is not None:
           #         raise Exception("Only one speed per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.speed = convert_str_to_int(child.text)


           elif tag == "monsterluck":
               if self.luck_pool is not None:
                   raise Exception("Only one luck per monster. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   self.luck_pool = child.text

           # elif tag == "perception":
           #     if self.perception is not None:
           #         raise Exception("Only one perception per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.perception = convert_str_to_int(child.text)

           # elif tag == "will":
           #     if self.will is not None:
           #         raise Exception("Only one will per monster. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         self.will = convert_str_to_int(child.text)

           elif tag == "abilityref":
               ref = AbilityRef()
               ref.parse(child)
               self.ability_refs[ref.get_id()] = ref

           elif tag == "variant":
               variant = MonsterVariant(self)
               variant.parse(child)
               self.variants.append(variant)

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
                   self.description = children_to_string(child)

           elif is_comment(child):
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) in file %s\n" % 
                               (child.tag, self.fname))
        #self.validate()
        return


if __name__ == "__main__":

    src_dir = abspath(join(dirname(__file__)))
    root_dir = abspath(join(src_dir, ".."))    
    
    monster_groups = MonsterGroups()
    monster_groups_dir = join(root_dir, "monsters")
    monster_groups.load(monster_groups_dir, fail_fast=True)
    
    # build_dir = join(root_dir, "build")
    # #monster_groups.draw_all_skill_trees(build_dir)
    # #monster_groups.draw_skill_tree(build_dir)
    # #monster_groups.draw_skill_tree2(build_dir)

    for monster_group in monster_groups:

        for monster in monster_group:
            print(monster)
            print(monster.get_id())
            print(monster.get_ac())

            if monster.get_id() == "human.thug":
                assert monster.get_ac() is not None

    #         if "eering" not in monster.get_title():
    #             continue
            
    #         print("\t%s" % monster.get_title())
    #         print("\t\t\tMonster Class: %s" % monster.get_monster_class())
    #         print("\t\t\tMonster Desc: %s" % monster.description)
    #         #print("\t\t\tMonster Class: %s" % monster.get_monster_class())
    #         #print("\t\t\t\t: %s" % monster.get_monster_class())
            
    #         for monster_rank in monster.get_ranks():
    #             print("\t\t\t\t%s" % monster_rank.get_title())
    #             print("\t\t\t\t%s" % monster_rank.check)
    #             print("\t\t\t\t%s" % monster_rank.description)
    #         #    #print("\t\t\tLore: %s" % monster_rank.get_default_lore())



