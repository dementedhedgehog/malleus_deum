#!/usr/bin/env python
"""

  This represents the game state.
  It's kind of an umbrella object that contains a bunch of little tables.

"""
import re
from os.path import abspath, join, splitext, dirname, exists, basename
from os import walk

from abilities import AbilityGroups # , ability_families
from monsters import MonsterGroups
from archetypes import Archetypes
from encounters import Encounters
from patrons import Patrons
from npcs import NPCGangs
from attribute_bonuses import attribute_bonuses
from changelog import Changelog
from licenses import Licenses
from weapons import Weapons
from utils import split_ability_tokens



ability_ref_parser = re.compile(
    # ability prefix (one or two "special stars")
    r"✱"
    r"(?P<is_unranked_ability_id>✱?)"
    # optional ability group
    #"((?P<ability_group>[a-zA-Z]+)\.)?"
    # mandatory ability name (can't end in _)
    r"(?P<ability_name>[a-zA-Z_]*[a-zA-Z])"
    # optional alternate way to write specialization
    r"(\.(?P<ability_specialization2>[a-zA-Z]+))?"
    # optional specialization
    r"(\[(?P<ability_specialization>[a-zA-Z_0-9\-\?/ ]+)\])?"
    # optional rank
    r"(_(?P<rank>[0-9]+))?" 
)    



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
        return

    def load(self, root_dir, fail_fast=True):

        # load the version
        changelog_dir = join(root_dir, "docs")
        changelog_fname = join(changelog_dir, "changelog.xml")
        changelog = Changelog.load(changelog_fname)
        self.version = changelog.get_version()
        
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


    def parse_ability_ranks(self, xml):
        """
        Given an xml string with *valid* ability references (e.g. ✱✱dagger.strike)
        or ability_rank references (e.g.  ✱dagger.strike_1) return a list of
        ability_ranks (and ignore any unranked ability references).  This doesn't
        do much in the way of error reporting.   Errors should have already been
        found when we're trying to build the archtypes with the filter_abilities
        method below.

        """
        # split on ability refs and newlines
        tokens = split_ability_tokens(xml)
        ability_ranks = []
        ability_specializations = []

        #print("X")
        for token in tokens:
            #print("TOKEN: %s\n" % token)
            
            # we don't need to process things that are not ability rank references
            if not token.startswith("✱") or token.startswith("✱✱"):
                continue
            
            ability_ref_match = ability_ref_parser.match(token)

            if type(ability_ref_match) is not re.Match:
                raise Exception(f"Can't parse ability ref {token}")

            # try and translate the token...
            # if it starts with two ✱✱ it's an ability id (i.e. it's supposed to be rankless)
            # if it starts with one it's an ability_rank id.
            ability_ref = ability_ref_match.groupdict()
            is_unranked_ability_id = ability_ref.get("is_unranked_ability_id") is not None

            #print(" ABILITY REF %s " % ability_ref)

            # get the parts..
            ability_name = ability_ref.get("ability_name")
            specialization = ability_ref.get("ability_specialization") or ability_ref.get("ability_specialization2")
            if not specialization:
                # ignore specializations for now
                #ability_specializations.append(
                continue
            #print(f"SPECIALIZATION %s\n" % specialization)
            rank = ability_ref.get("rank", "")
            # rankless_ability_id = f"{ability_name}"

            # ability = self.ability_groups.get_ability(ability_name)
            # try:
            #     _id = ability.get_id()
            # except KeyError:
            #     raise Exception()
            # print(_id)

            _id = f"{ability_name}_{rank}"

            #print("TOKEN: %s\n" % token)
            
            #try: 
            # check if the ability exists, and if it exists check if it has the given rank.
            try:
                ability_rank = self.ability_groups.get_ability_rank(_id)
            except KeyError:
                print("--- XML: %s\n" % xml)
                print("--- TOKEN: %s\n" % token)
                print("ID %s\n" % _id)
                import sys
                sys.exit()
            
            #except KeyError as e:
            #    print(e)

            ability_ranks.append(ability_rank)
            
        return ability_ranks

    
    def filter_abilities(self, xml, verbose=False):
        """
        Filters xml replacing our "magical" ability references (e.g. ✱✱dagger.strike)
        or ability_rank references (e.g.  ✱dagger.strike_1), with values from the db. 

        This is a pretty hacky but convenient approach. We could have done this with
        xml or jinja filters, but it's a lot of typing.

        """
        # split on ability refs and newlines
        tokens = split_ability_tokens(xml)
        
        new_tokens = []
        line_number = 1
        
        for token in tokens:
                
            # ability refs are tokens that start with the special character ✱
            # we don't need to process things that are not ability refs
            if not token.startswith("✱"):
                new_tokens.append(token)
                if token == "\n":
                    line_number += 1
                continue

            ability_ref_match = ability_ref_parser.match(token)

            if type(ability_ref_match) is not re.Match:
                raise Exception(f"Can't parse ability ref {token}")
            
            # try and translate the token...
            # if it starts with two ✱✱ it's an ability id (i.e. it's supposed to be rankless)
            # if it starts with one it's an ability_rank id.
            ability_ref = ability_ref_match.groupdict()
            is_unranked_ability_id = ability_ref.get("is_unranked_ability_id") is not None
            
            # get the parts..
            ability_name = ability_ref.get("ability_name")
            specialization = ability_ref.get("ability_specialization")
            rank = ability_ref.get("rank", "")
            rankless_ability_id = f"{ability_name}"

            # Some default and informative "Can't find ability" message for the _id
            _id = f"Unable to look up ability id for ability name: {ability_name}"

            try:
                ability = self.ability_groups.get_ability(ability_name)
                if ability is None:
                    raise KeyError(f"Unable to look up ability for ability name: {ability_name}")

                try:
                    _id = ability.get_id()
                except KeyError:
                    raise Exception()

                # check if the ability exists, and if it exists check if it has the given rank.
                if is_unranked_ability_id:
                    self.ability_groups.get_ability(_id)
                else:
                    self.ability_groups.get_ability_rank(_id)

            except KeyError:
                #
                # Here we do quite a bit of work to provide useful contextual information
                # when we fail to lookup the given ability or ability rank id.
                #

                # build debug context..
                start = max(line_number-8, 0)
                end = min(line_number+8, len(tokens))
                # truncate the debug context if it's too long.
                before = "".join(tokens[start:line_number])[-60:]
                after = "".join(tokens[line_number+1:end])[:60]
                context = f"On line: {line_number} {before} ❰{token}❱ {after}"

                # it's bad, so try dropping the rank and looking for the ability
                # (so we can log some extra debug info)
                try:
                    self.ability_groups.get_ability(_id)
                except KeyError:
                    # Bad ability
                    raise Exception(
                        f"Invalid ability id {rankless_ability_id} in reference {_id}. "
                        f"Check the ability is exists and not misspelled.\n{context}"
                    ) from None
                else:
                    # Check the ability group exists
                    ability_group_regex = re.compile("^(?P<ability_group>[^.]*?)\.")
                    match = ability_group_regex.search(_id)
                    print(f"ID {_id}  Match {str(match)}")
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

                    if not is_unranked_ability_id:
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
            specialization_str = f' specialization="{specialization}"' if specialization is not None else ''
            rank_str = f' rank="{rank}"' if rank is not None else ''
            ability_ref_xml = f'<abilityref id="{rankless_ability_id}"{rank_str}{specialization_str}/>'

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
    import sys
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
        
        
