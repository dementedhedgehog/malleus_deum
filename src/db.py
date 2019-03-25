#!/usr/bin/env python
"""

  This represents the game state.


"""
from os.path import abspath, join, splitext, dirname, exists, basename

from abilities import AbilityGroups
from abilities import SKILL_POINT_TYPE
from monsters import MonsterGroups
from archetypes import Archetypes
from patrons import Patrons
from npcs import NPCGangs
from attribute_bonuses import attribute_bonuses
from version import Version
from licenses import Licenses
from weapons import Weapons


class DB:

    def __init__(self):
        self.version = None
        self.patrons = None
        self.ability_groups = None
        self.monster_groups = None
        self.archetypes = None
        self.attribute_bonuses = attribute_bonuses
        self.skill_point_type = SKILL_POINT_TYPE
        self.licenses = None
        self.melee_weapons = None
        self.missile_weapons = None
        return

    # def get_x(self):
    #     return "X"
    
    def load(self, root_dir, fail_fast=True):

        # load the version
        version_dir = join(root_dir, "docs")
        version_fname = join(version_dir, "version.xml")
        self.version = Version.load(version_fname)
        
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

        # licenses
        resource_dir = join(root_dir, "resources")
        unused_resource_dir = join(root_dir, "unused_resources")
        self.licenses = Licenses()
        self.licenses.load((resource_dir, unused_resource_dir))

        # melee weapons
        melee_weapons_xml = join(root_dir, "items", "melee_weapons.xml")
        self.melee_weapons = Weapons(fname=melee_weapons_xml)
        self.melee_weapons.load()        
    
        # missile weapons
        missile_weapons_xml = join(root_dir, "items", "missile_weapons.xml")
        self.missile_weapons = Weapons(fname=missile_weapons_xml)
        self.missile_weapons.load()

        assert self.missile_weapons is not None
        return

