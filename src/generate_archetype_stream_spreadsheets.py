#!/bin/env python3
"""

  Generate some info so we can manage archetype abilities and game balance.
 

"""
import sys
from collections import defaultdict
from os.path import abspath, join, splitext, dirname, exists, basename


src_dir = abspath(join(dirname(__file__)))
sys.path.append(src_dir)

import datetime
import xlsxwriter



from archetypes import Archetypes
from abilities import AbilityGroups, Ability
from utils import (
    root_dir,
    build_dir,
    abilities_dir,
    )



def write_archetype_stream_spreadsheet(
        spreadsheet_fname,
        ability_groups,
        archetype):
    
    workbook = xlsxwriter.Workbook(spreadsheet_fname)
    worksheet = workbook.add_worksheet()

    # for each stream we want to know how full the stream is at each level.
    stream_config = archetype.get_stream_config()
    all_streams = stream_config.walk()

    abilities = list(ability_groups.get_abilities())
    for ability in abilities:
        print(f"ABILIY .. {ability}")
        assert type(ability) == Ability
        
    stream_config.resolve_abilities("frog", abilities)
    print(f"----------------------------------- {archetype.get_title()}")
    for stream in all_streams:        
        print(f"----------------------------------- {stream.title}")
        print(f"----------------------------------- {sorted([a.title for a in stream.resolved_abilities])}\n\n")


    # things we want to check...
    # don't overflow any stream?
    # conflicts with a given ability
    capacity_lookup = defaultdict(float)
    for stream in all_streams:
        for level in archetype.levels:
            for ability in stream.resolved_abilities:
                for branch in level.branches:
                    capacity = branch.get_capacity(ability)
                    print(f"{stream} {ability} {level} {capacity}")

                    capacity_lookup[ability.get_id()] += capacity
                    print(f"===={ability.get_id()}")



    for ability_id, capacity in capacity_lookup.items():
        print(f"- {ability_id} {capacity}")

            
            
        
        # for branch in level.branches:
        #     print(branch)
    
    # #
    # LABEL_COL = 1

    # r = 1
    # c = LABEL_COL

    # worksheet.write(r, c, "Level"); c += 1
    # for level in range(1, 10):
    #     worksheet.write(r, c, level); c += 1

    # ABILITY_LABEL_COL = 2
    # r += 2
    # for ability_group in ability_groups:
    #     worksheet.write(r, LABEL_COL, ability_group.get_title())        
    #     r += 1

    #     for ability in ability_group:
    #         worksheet.write(r, ABILITY_LABEL_COL, ability.get_title())
    #         r += 1

    # r += 2
    # c = LABEL_COL
    
    # for archetype in archetypes:
    #     worksheet.write(r, c, archetype.get_title())
    #     # c += 1
    #     r += 1
        
    # workbook.close()
    return
        



        
if __name__ == "__main__":
    # load the game database (archetypes, abilties etc).

    fail_fast = True

    ability_groups = AbilityGroups()
    ability_groups.load(abilities_dir, fail_fast=fail_fast)


    # load the archetypes
    archetype_dir = join(root_dir, "archetypes")
    archetypes = Archetypes()
    archetypes.load(ability_groups=ability_groups,
                    archetypes_dir=archetype_dir, fail_fast=fail_fast)
        

    archetype_id = "night_gauner"
    archetype = archetypes[archetype_id]
    
    
    spreadsheet_fname = join(build_dir, archetype_id + "_streams.xls")
    write_archetype_stream_spreadsheet(spreadsheet_fname,
                                       ability_groups,
                                       archetype)
    
