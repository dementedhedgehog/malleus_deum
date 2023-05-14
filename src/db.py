#!/usr/bin/env python
"""

  This represents the game state.
  It's kind of an umbrella object that contains a bunch of little tables.

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


    def lookup_ability_or_ability_rank(self, ability_id, rank_id):
        """Check the ability id exists in our db."""
        try:
            ability_rank = self.ability_groups.get_ability_rank(ability_id, rank_id)
            return ability_rank
        except KeyError:
            return self.ability_groups.get_ability(ability_id)


    def filter_abilities(self, xml):
        """
        Filters xml replacing our "magical" ability references (e.g. ✱✱dagger.strike)
        or ability_rank references (e.g.  ✱dagger.strike_1), with values from the db. 

        This is a pretty hacky but convenient approach. We could have done this with
        xml or jinja filters, but it's a lot of typing.

        """
        templates_regex = re.compile("\[(?P<template>.*?)\]")        
        ability_group_regex = re.compile("^(?P<ability_group>[^.]*)\.")
        tokens = re.split(
            "("
            "(?:"
            "✱✱?"                          # ability prefix
            "(?:[a-zA-Z]+\.)?"             # optional ability group
            "[a-zA-Z_]*[a-zA-Z]"           # mandatory ability name (can't end in _)
            "(?:\[[a-zA-Z_0-9\-\?/ ]+\])?" # optional template
            "(?:_[0-9]+)?"                 # optional rank
            ")"
            "|(?:\n)"                      # we also split on newlines (for line numbers).
            ")",
            xml)
        new_tokens = []
        line_number = 1
        
        for i, token in enumerate(tokens):

            # ability refs are tokens that start with the special character ✱
            if not token.startswith("✱"):
                new_tokens.append(token)
                if token == "\n":
                    line_number += 1                
                continue            
            
            # try and translate the token...
            # if it starts with two ✱✱ it's an ability id (i.e. it's supposed to be rankless)
            # if it starts with one it's an ability_rank id.
            is_ability_id = token.startswith("✱✱")
            
            # first drop leading ✱'s
            stripped_token = token.lstrip("✱")

            # try and find template info..
            match = templates_regex.search(token)
            if match is not None:                        
                template = match.group("template")
            else:
                template = None

            # remove template info if there is any
            # e.g. ✱social.etiquette[Dwarven]_3 --> social.etiquette_3
            # (no abilities should have templated abilities as prereqs).
            _id = templates_regex.sub("", stripped_token)

            # strip out the rank.. as well
            rankless_ability_id, rank = get_ability_rank(_id)

            try: 
                # check if the ability exists, and if it exists check if it has the given rank.
                if is_ability_id:
                    self.ability_groups.get_ability(_id)
                else:
                    self.ability_groups.get_ability_rank(_id)

            except KeyError:

                #
                # Here we do quite a bit of work to provide useful contextual information
                # when we fail lookup the given ability or ability rank id.
                #

                # build debug context..
                start = max(i-8, 0)
                end = min(i+8, len(tokens))
                # truncate the debug context if it's too long.
                before = "".join(tokens[start:i])[-60:]
                after = "".join(tokens[i+1:end])[:60]
                context = f"On line: {line_number} {before} ❰{token}❱ {after}"

                # it's bad, so try dropping the rank and looking for the ability
                # (so we can log some extra debug info)
                try:
                    self.ability_groups.get_ability(rankless_ability_id)
                except KeyError:
                    # Bad ability
                    raise Exception(
                        f"Invalid ability id {rankless_ability_id} in reference {_id}. "
                        f"Check the ability is exists and not misspelled.\n{context}"
                    ) from None
                else:                
                    # Check the ability group exists
                    match = ability_group_regex.search(_id)
                    if match is not None:                        
                        ability_group_name = match.group("ability_group")
                        ability_group = self.ability_groups.get_ability_group(ability_group_name)
                        if ability_group is None:
                            # Then it must be a missing/misspelled ability group
                            raise Exception(
                                "Invalid ability_rank_id in reference. \n"
                                f"Ability Group {ability_group_name} does not exist or is "
                                f"mispelled in {_id}.\n{context}"
                            ) from None

                    # Check the ability exists.
                    if self.ability_groups.get_ability(_id) is None:
                        # Then it's a missing/misspelled ability
                        raise Exception(
                            f"Missing/misspelled ability? {rankless_ability_id} in {_id}."
                            f"\n{context}"
                        ) from None

                    if not is_ability_id:
                        # We're looking for an ability_rank id (not an ability id).
                        # so we can check a few more things..

                        # Do we have an ability rank?
                        if rank is None:
                            # Then it must be a bad ability rank
                            raise Exception(
                                f"Invalid rank '{rank}' in ability_rank reference."
                                f"\n{context}"
                            ) from None
                        else:
                            # Dunno!?
                            raise Exception(
                                "Bug in db.py !! looking up ability. "
                                f"Ability rank out of range? {_id}.\n{context}"
                            ) from None

                        # it's bad, so try dropping the rank and looking for the ability
                        # (so we can log some extra debug info)
                        try:
                            self.ability_groups.get_ability(rankless_ability_id)
                        except KeyError:
                            # Bad ability
                            raise Exception(
                                f"Invalid ability id in reference {_id}. "
                                f"Check the ability rank is valid.\n{context}"
                            ) from None
                        else:
                            # Dunno!?
                            raise Exception(
                                "Bug in db.py !! looking up ability. "
                                f"Ability rank out of range? {rank} in {_id}. "
                                f"\n{context}"
                            ) from None


            # Build the abilityref xml element 
            template_str = f' template="{template}"' if template is not None else ''
            rank_str = f' rank="{rank}"' if rank is not None else ''
            ability_ref_xml = f'<abilityref id="{rankless_ability_id}"{rank_str}{template_str}/>'

            # and insert the abilityref xml into the stream of tokens we're parsing.
            new_tokens.append(ability_ref_xml)
        return "".join(new_tokens)


__ability_rank_regex = re.compile("_[0-9]+$")
def get_ability_rank(ability_id):
    """Takes an ability id like ✱luck.lucky_1" and returns a tuple ("✱luck.lucky", "1")"""
    rankless_ability_id = __ability_rank_regex.sub("", ability_id)
    ranks = __ability_rank_regex.findall(ability_id)
    rank = ranks[0].lstrip("_") if len(ranks) > 0 else None
    return rankless_ability_id, rank
    
    
if __name__ == "__main__":

    # Just some test code.. (should be in a unit test if I were doing this properly).
    import utils
    db = DB()
    db.load(utils.root_dir)
    #print(db.filter_abilities("this is a test ✱social.etiquette[Church-of-Mithras]_2 and so forth"))
    print(db.filter_abilities("this is a test ✱social.etiquette[x y]_2 and so forth"))
