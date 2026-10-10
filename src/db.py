#!/usr/bin/env python
"""
  This represents the ttrpg game state.

  The "db" is basically configuration in a bunch of xml files.  The db is handed
  to the code that process the docs. It's kind of an umbrella object that
  contains a bunch of little tables.

"""
#import re
from os.path import abspath, join, splitext, dirname, exists, basename
from os import walk

from abilities import AbilityGroups
from monsters import MonsterGroups
from archetypes import Archetypes
from encounters import Encounters
from patrons import Patrons
from npcs import NPCGangs
from attribute_bonuses import attribute_bonuses
from changelog import Changelog
from resources import Resources
from weapons import Weapons
from utils import split_ability_tokens
from schema_introspection import Constants


class DB:

    def __init__(self):
        self.version = None
        self.patrons = None
        self.ability_groups = None
        self.monster_groups = None
        self.archetypes = None
        self.attribute_bonuses = attribute_bonuses
        self.resources = None
        self.melee_weapons = None
        self.missile_weapons = None
        self.encounters = None
        self.constants = None
        return

    def load(self, root_dir, fail_fast=True):
        """
        Reads the ttrpg game data from a set of xml files.

        """
        # load the version
        changelog_dir = join(root_dir, "docs")
        changelog_fname = join(changelog_dir, "changelog.xml")
        changelog = Changelog.load(changelog_fname)
        self.version = changelog.get_version()
        
        # load the abilities
        abilities_dir = join(root_dir, "abilities")
        self.ability_groups = AbilityGroups()
        self.ability_groups.load(abilities_dir, fail_fast=fail_fast)
        
        # load the archetypes
        archetype_dir = join(root_dir, "archetypes")
        self.archetypes = Archetypes()
        self.archetypes.load(ability_groups=self.ability_groups,
                             archetypes_dir=archetype_dir, fail_fast=fail_fast)

        # load the monsters
        monsters_dir = join(root_dir, "monsters")
        self.monster_groups = MonsterGroups()
        self.monster_groups.load(monsters_dir, fail_fast=fail_fast)

        # load the patrons
        patrons_dir = join(root_dir, "patrons")
        self.patrons = Patrons()
        self.patrons.load(patrons_dir=patrons_dir,
                          ability_groups=self.ability_groups,
                          fail_fast=fail_fast)

        # load the npcs
        npcs_dir = join(root_dir, "npcs") 
        self.npc_gangs = NPCGangs()        
        self.npc_gangs.load(npcs_dir=npcs_dir,
                            monster_groups=self.monster_groups,
                            fail_fast=fail_fast)

        # resources
        self.resources = Resources()
        resource_dirs = []
        for root, dirs, files in walk(root_dir):
            for d in dirs:
                if d == "resources":                    
                    resource_dirs.append(join(root, d))
        self.resources.load(resource_dirs)

        # melee weapons
        melee_weapons_xml = join(root_dir, "items", "melee_weapons.xml")
        self.melee_weapons = Weapons(fname=melee_weapons_xml)
        self.melee_weapons.load()        
    
        # missile weapons
        missile_weapons_xml = join(root_dir, "items", "missile_weapons.xml")
        self.missile_weapons = Weapons(fname=missile_weapons_xml)
        self.missile_weapons.load()

        # load the encounters
        encounters_dirs = join(root_dir, "encounters")
        self.encounters = Encounters()
        self.encounters.load(root_dir=root_dir)

        # load the constants (to expose to Jinja mainly)
        self.constants = Constants.get_constants()

        # The schema introspection can't get all the information we need,
        # (doesn't expose information outside of rpg.xsd, and I'm not sure it
        # expands groups in the rpg.xsd file).
        for ability in self.ability_groups.get_abilities():
            raw_id = ability.get_id()
            name = ability.get_name()
            self.constants.set_constant("ABILITY_", raw_id, name)
        return


    def __getattr__(self, name):
        """
        Expose the constants dict.

        """
        return self.constants.__getattr__(name)
    
    def get_ability_from_ref(self, ability_ref):
        return self.ability_groups.get_ability(ability_ref._id)

    def get_ability_from_id(self, ability_id):
        return self.ability_groups.get_ability(ability_id)        
        
    #
    # Implement the Context Manager Protocol so we
    # can write the used resources interface.
    #
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.resources:
            self.resources.write_used_resources_db()
        return
    
    
if __name__ == "__main__":
    # Just some scratch test code used for debugging..
    #import sys
    import utils
    db = DB()
    db.load(utils.root_dir)
    # for fname in sys.argv[1:]:
    #     with open(fname) as f:
    #         xml = f.read()
    #         db.filter_abilities(xml, verbose=True)
    #db.filter_abilities("xxx ✱social.contacts[Church-of-Mithras]_2, ✱social.contacts.ettiquette[Church-of-Mithras]_2, xxxx", verbose=True)
    #db.filter_abilities("xxx ✱mace_strike_2, xxxx", verbose=True)
    #print(db.parse_ability_ranks("xxx ✱speed.jump ✱mace_strike_2, xxxx")) # , verbose=True)

    # from collections import defaultdict
    # ability_ids = defaultdict(list)
    #for g in db.ability_groups:
    #     print(g)
    #     for a_id, a in g.abilities.items():
    #         ability_ids[a.get_name()].append(a_id)

    # ability_names = sorted(ability_ids.keys())
    # for ability_name in ability_names:
    #     print(f"{ability_name}  ===> {ability_ids.join(', ')}")
        
        
    print(db.get_list_of_unused_art())
