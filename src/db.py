#!/usr/bin/env python
"""

  This represents the game state.


"""
import re
from os.path import abspath, join, splitext, dirname, exists, basename
from os import walk

from abilities import AbilityGroups, ability_families
from monsters import MonsterGroups
from archetypes import Archetypes
from encounters import Encounters
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
        self.licenses = None
        self.melee_weapons = None
        self.missile_weapons = None
        self.encounters = None
        self.ability_families = ability_families
        return

    def load(self, root_dir, fail_fast=True):

        # load the version
        version_dir = join(root_dir, "docs")
        version_fname = join(version_dir, "version.xml")
        self.version = Version.load(version_fname)
        
        # load the abilities
        print("Loading abilities")
        abilities_dir = join(root_dir, "abilities")
        self.ability_groups = AbilityGroups()
        self.ability_groups.load(abilities_dir, fail_fast=fail_fast)
        print("Abilities Loaded")
        
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

        # licenses
        self.licenses = Licenses()
        resource_dirs = []
        for root, dirs, files in walk(root_dir):
            for d in dirs:
                if d == "resources":                    
                    resource_dirs.append(join(root, d))
        unused_resource_dir = join(root_dir, "unused_resources")
        resource_dirs.append(unused_resource_dir)
        self.licenses.load(resource_dirs)

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
        
        assert self.missile_weapons is not None
        return


    def lookup_ability_or_ability_level(self, ability_id):
        try:
            ability_level = self.ability_groups.get_ability_level(ability_id)
            return ability_level
            #ability_str = ability_level.get_title()
        except KeyError:
            return self.ability_groups.get_ability(ability_id)
        #     ability = self.ability_groups.get_ability(ability_id)
        #     return ability
        #     if ability is not None:
        #         ability_str = ability.get_title()
        #     else:
        #         # dunno what this is .. just pass it through unmodified.
        #         ability_str = ability_id
        # return ability_str
        

    def filter_abilities(self, xml):
        """
        Filters xml replacing magical ability references (starting with '✱')
        with values from the db.  We could have done this with xml or jinja
        filters but it's a lot of typing.

        """
        templates_regex = re.compile("\[.*?\]")
        ability_group_regex = re.compile("^(?P<ability_group>[^.]*)\.")
        ability_level_regex = re.compile("_[0-9]+$")
        tokens = re.split("(✱[a-zA-Z]+\.[a-zA-Z_0-9\-\?\[\]]+)", xml)
        new_tokens = []
        for i, token in enumerate(tokens):

            # ability refs are tokens that start with the special character ✱
            if not token.startswith("✱"):
                new_tokens.append(token)
                continue
            
            # try and translate the token (drop leading ✱)
            ability_level_id = token[1:]

            # remove template info if there is any
            # e.g. ✱social.etiquette[Dwarven]_3 --> social.etiquette_3
            # (no abilities should have templated abilities as prereqs).
            ability_level_id = templates_regex.sub("", ability_level_id)
            
            # check if this is a good valid ability level id?
            try:
                self.ability_groups.get_ability_level(ability_level_id)
            except KeyError:

                # build debug context..
                start = max(i -3, 0)
                end = min(i + 3, len(tokens))
                # truncate context in case it's big.
                before = " ".join(tokens[start:i])[-50:]
                after = " ".join(tokens[i+1:end])[:50]
                context = f"{before} ❰{token}❱ {after}"
                                
                # it's bad, so try dropping the level and looking for the ability
                # (so we can log some extra debug info)
                ability_id = ability_level_regex.sub("", ability_level_id)
                try:
                    self.ability_groups.get_ability(ability_id)
                except KeyError:
                    # Bad ability
                    raise Exception(
                        f"Invalid ability id in reference {ability_id}. "
                        f"Check the ability level is valid. Near:\n{context}")
                else:

                    # Check the ability group exists
                    match = ability_group_regex.search(ability_level_id)
                    if match is not None:                        
                        ability_group_name = match.group("ability_group")
                        print(f"... {token} ----- {ability_group_name} ------------------- ")
                        ability_group = self.ability_groups.get_ability_group(ability_group_name)
                        if ability_group is None:
                            # Then it must be a missing/misspelled ability group
                            raise Exception(
                                "Invalid ability_level_id in reference. \n"
                                f"Ability Group {ability_group_name} does not exist or is mispelled "
                                f"in {ability_level_id}. Near:\n{context}")


                    # Check the ability exists.
                    if self.ability_groups.get_ability(ability_id) is None:
                        # Then it's a missing/misspelled ability
                        raise Exception(
                            f"Missing/misspelled ability! {ability_id} in {ability_level_id}. Near:\n{context}")
                                                
                    # Do we have an ability level?
                    if ability_level_regex.search(ability_level_id):
                        # Then it must be a bad ability level
                        raise Exception(
                            "Invalid ability_level_id in reference. "
                            f"Ability level out of range? {ability_level_id}. Near:\n{context}")
                    else:
                        # Dunno!?
                        raise Exception(
                            "Bug in db.py !! looking up ability. "
                            f"Ability level out of range? {ability_level_id}. Near:\n{context}")
            
            ability_ref_xml = f'<abilityref id="{ability_level_id}"/>'
            new_tokens.append(ability_ref_xml)
        return "".join(new_tokens)
