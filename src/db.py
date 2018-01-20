#!/usr/bin/env python
"""

  This represents the game state.


"""
from os.path import abspath, join, splitext, dirname, exists, basename

from abilities import AbilityGroups
from monsters import MonsterGroups
from archetypes import Archetypes
from patrons import Patrons
from npcs import NPCGangs
from attribute_bonuses import attribute_bonuses


class DB:

    def __init__(self):
        self.patrons = None
        self.ability_groups = None
        self.monster_groups = None
        self.archetypes = None
        self.attribute_bonuses = attribute_bonuses
        return

    
    def load(self, root_dir, fail_fast=True):
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
        npcs_dir = join(root_dir, "encounters") # FIXME
        self.npc_gangs = NPCGangs()        
        self.npc_gangs.load(npcs_dir=npcs_dir,
                            monster_groups=self.monster_groups,
                            fail_fast=fail_fast)
        return

