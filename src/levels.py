"""
  Defines classes used to control and visualize the 
  abilities an archetype can have.

"""
import sys
import re

import traceback

from utils import (
    COMMENT,
    normalize_ws,
    contents_to_string,
    convert_str_to_int,
    split_ability_tokens,
    )

split_regex = re.compile(",\s*")

ALL_OF = -1
GAIN = 0  # synonym for ALL_OF, worded differently in docs
CHOICES = {
    "all-of": ALL_OF,
    "gain": GAIN, # choose one out of a list of one (we translate it differently).
    "one-of": 1,
    "two-of": 2,
    "three-of": 3,
    "choice": 1, # DEPRECATED
}


class LevelAbilityStats:
    """
    Used to summarize the range of level abilities we expect for an archetype level.
    We want this information to help us build and balance level progression for archetypes.

    """
    def __init__(self):
        self.min_rank = sys.maxsize
        self.max_rank = 0
        self.max_count = 0
        self.min_count = sys.maxsize


    def __str__(self):
        return f"Ranks:{self.min_rank}-{self.max_rank}, Counts:{self.min_count}-{self.max_count}"


    def merge(self, stats):
        if stats.max_rank > self.max_rank:
            self.max_rank = stats.max_rank

        if stats.min_rank < self.min_rank:
            self.min_rank = stats.min_rank

        if stats.max_count > self.max_count:
            self.max_count = stats.max_count

        if stats.min_count < self.min_count:
            self.min_count = stats.min_count
        return 
                


class Choice:
    """
    The player has to choose between some abilities.
    For archetype descriptions

    """
    def __init__(self, number_to_choose=ALL_OF):  # FIXME: at some point force this to be specified
        self.ability_level_ids = []
        self.number_to_choose = number_to_choose
        self.contents = None

    def load(self, choice_node, fname, fail_fast):
        self.contents = contents_to_string(choice_node)          
        self.ability_level_ids = split_regex.split(self.contents)
        return

    def __str__(self):
        return f"Choice: {self.contents}"


    def get_stats(self, db, ability_filter):
        stats = LevelAbilityStats()
        for ability in db.parse_ability_ranks(self.contents):
            if ability_filter(ability):
                rank = ability.get_rank_number()
                if rank < stats.min_rank:
                    stats.min_rank = rank

                if rank > stats.max_rank:
                    stats.max_rank = rank

                stats.max_count += 1
        stats.min_count = stats.max_count
        return stats
    


class OrChoice:
    """
    Poorly thought out code to allow OR of two or more sets of choices.
    We're always allowed to choose one and only one of these.
    For archetype descriptions.

    """
    def __init__(self):
        self.choices = []

    def load(self, or_choice_node, fname, fail_fast):
        # we only allow one level of ors.. we don't need to worry about recursion here.
        for child in list(or_choice_node):
           tag = child.tag
           if tag in CHOICES:
               number_to_choose = CHOICES[tag]
               choice = Choice(number_to_choose=number_to_choose)
               choice.load(child, fname, fail_fast)
               self.choices.append(choice)

           elif tag == "or":
               raise Exception("WE DONT ALLOW RECURSIVE `OR' ELEMENTS HERE! XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))        

           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))        
        return


    def get_stats(self, db, ability_filter):
        stats = LevelAbilityStats()
        for choice in self.choices:
            choice_stats = choice.get_stats(db, ability_filter)
            stats.merge(choice_stats)
        return stats
    
    
class Path:
    """
    Represents one choice in a branch.
    For archetype descriptions

    """
    def __init__(self):
        # a list of ability level ids.
        self.title = None
        self.choices = [] # this is a list of Choice or OrChoice nodes.
        self.chance = None

    def load(self, path_node, fname, fail_fast):

        if "chance" not in path_node.attrib:
            raise Exception("Path missing chance attribute (%s) File: %s Line: %s\n" % 
                            (path_node.tag, fname, path_node.sourceline))

        self.chance = path_node.attrib.get("chance")

        # handle all the children
        for child in list(path_node):        
           tag = child.tag
           if tag == "pathtitle":
               self.title = contents_to_string(child)

           elif tag in CHOICES:
               number_to_choose = CHOICES[tag]
               choice = Choice(number_to_choose=number_to_choose)
               choice.load(child, fname, fail_fast)
               self.choices.append(choice)

           elif tag == "or":
               or_choice_node = OrChoice()
               or_choice_node.load(child, fname, fail_fast)
               self.choices.append(or_choice_node)
                          
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return

    
    def __str__(self):
        return "Choice: " + ", ".join([str(c) for c in self.choices])


    def get_capacity(self, ability):
        # for each level we can either get the ability at various levels
        # or we cannot.
        #print(f"\t{self.choices} {ability}")

        prefix = f"✱{ability.ability_id}"
        
        #print(f"\t{', '.join([str(c) for c in self.choices])} --> {ability}")
        
        #return 1 if ability in self.choices else 0
        print("----")
        for choice in self.choices:
            print(f"\t--{choice} {[x for x in choice.ability_level_ids]}")
            for choice_ability_level_id in choice.ability_level_ids:
                print(f"\t\t--{choice_ability_level_id}")
                if choice_ability_level_id is not None:
                    print(f"PREFIX {prefix} CHOICE ALID {choice_ability_level_id}")
                    if prefix in choice_ability_level_id:
                        return 1
        return 0

    

    
class Branch:
    """
    One set of paths to choose from.  The player chooses one Path from each Branch.

    """
    def __init__(self):
        self.title = None
        self.description = None
        self.paths = []

    def load(self, branch_node, fname, fail_fast):

        # handle all the children
        for child in list(branch_node):
        
           tag = child.tag
           if tag in ("branchtitle", ):
               self.title = contents_to_string(child)
           
           elif tag == "branchdescription":
               # we don't care about these ones.. they're for human consumption.
               self.description = contents_to_string(child)
               pass

           elif tag == "path":
               path = Path()
               path.load(child, fname, fail_fast)
               self.paths.append(path)
                       
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return

    def get_capacity(self, ability):
        # take the maximum value for all paths.
        capacity = 0
        total_chance = 0.0
        for path in self.paths:
            capacity = max(capacity, path.get_capacity(ability))
            total_chance += path.chance
        return capacity / total_chance

    def __str__(self):
        return f"Branch: {self.title}\t" + ", ".join([str(p) for p in self.paths])


def filter_martial_abilities(ability):
    return True
    
        

class Level:

    def __init__(self):
        self.level_number = None
        self.mettle = None
        self.mettle_refresh = None
        self.stamina = None
        self.health = None
        self.health_refresh = None
        self.magic = None
        self.magic_refresh = None
        self.luck = None
        self.luck_refresh = None
        self.branches = []


    def _get_level_stats(self, db, ability_filter):
        print("Get Level Stats! --------------------------------------------- ")
        stats = LevelAbilityStats()
        for branch in self.branches:
            for path in branch.paths:
                for choice in path.choices:

                    choice_stats = choice.get_stats(db, ability_filter)
                    stats.merge(choice_stats)
        return stats
    
    def get_level_stats_for_martial_abilities(self, db):
        return self._get_level_stats(db, filter_martial_abilities)
    

    def load(self, level_node, fname, fail_fast):

        if "levelnumber" in level_node.attrib:
            self.level_number = level_node.attrib.get("levelnumber")
        
        # handle all the children
        for child in list(level_node):
        
           tag = child.tag
           if tag == "levelnumber":
               if self.level_number is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.level_number = int(child.text.strip())

           elif tag == "levelmettle":
               if self.mettle is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.mettle = contents_to_string(child)                   

           elif tag == "levelmettlerefresh":
               if self.mettle_refresh is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.mettle_refresh = contents_to_string(child)

           elif tag == "levelstamina":
               if self.stamina is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.stamina = normalize_ws(child.text.strip())

           # elif tag == "levelstaminarefresh":
           #     if self.stamina_refresh is not None:
           #         raise NonUniqueTagError(tag, fname, child.sourceline)
           #     else:
           #         self.stamina_refresh = normalize_ws(child.text.strip())

           elif tag == "levelhealth":
               if self.health is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                self.health = normalize_ws(child.text.strip())

           elif tag == "levelhealthrefresh":
               if self.health_refresh is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                self.health_refresh = normalize_ws(child.text.strip())

           elif tag == "levellore":
               if self.lore is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.lore = convert_str_to_int(child.text.strip())

           elif tag == "levelmartial":
               if self.martial is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.martial = convert_str_to_int(child.text.strip())

           elif tag == "levelgeneral":
               if self.general is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.general = convert_str_to_int(child.text.strip())

           elif tag == "levelmagic":
               if self.magic is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.magic = convert_str_to_int(child.text.strip())

           elif tag == "levelabilities":
               if len(self.level_abilities) > 0:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_abilities(child)

           elif tag == "levelpromotions":
               if len(self.level_promotions) > 0:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   if child.text is not None:
                       self.load_level_promotions(child)

           elif tag == "levelmagicpool":
               if self.magic is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.magic = contents_to_string(child)
                       
           elif tag == "levelmagicrefresh":
               if self.magic_refresh is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.magic_refresh = contents_to_string(child)

           elif tag == "levelluck":
               if self.luck is not None:
                   raise NonUniqueTagError(tag, self.fname, child.sourceline)
               else:
                   self.luck = contents_to_string(child)

           elif tag == "levelluckrefresh":
               if self.luck_refresh is not None:
                   raise NonUniqueTagError(tag, fname, child.sourceline)
               else:
                   self.luck_refresh = contents_to_string(child)
                       
           elif tag == "branch":
               # FIXME parse this later.
               branch = Branch()
               branch.load(child, fname, fail_fast)
               self.branches.append(branch)
                       
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))
        return

    
class Levels:
    """
    A list of level progression data for the Archetype.

    """
    def __init__(self):
        self.levels = []
        return

    def load(self, levels_node, fname, fail_fast):
        # handle all the children
        for child in list(levels_node):
        
           tag = child.tag
           if tag == "archetypelevel":
               level = Level()
               level.load(child, fname, fail_fast)
               self.levels.append(level)

           elif tag in ("subsection", ):
               # These are tags that don't contain archetype metadata.
               # They can be ignored here.
               pass
               
           elif tag is COMMENT:
               # ignore comments!
               pass
           
           else:
               raise Exception("UNKNOWN XML TAG (%s) File: %s Line: %s\n" % 
                               (child.tag, fname, child.sourceline))

        self.levels.sort(key = lambda lpd: lpd.level_number)
        return

    def add_level(self, level):
        self.levels.append(level)

    def __iter__(self):
        return iter(self.levels)

    def __getitem__(self, index):
        return self.levels[index]

    def get_level_by_level_number(self, level_number):
        
        i = level_number-1
        level = self.levels[i] if i < len(self.levels) else None

        #if level is not None:
        #    print(" LEVELs %s  I %s" % (self.levels, i))

        #traceback.print_stack()
        #print(" LEVELs LEN %s " % len(self.levels))
        #print(" LEVEL %s " % level)
        return level


