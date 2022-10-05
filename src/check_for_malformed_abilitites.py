#!/usr/bin/env python3
"""

   Checks the abilities for problems, a bit like lint.

"""
from os.path import abspath, join, dirname # , splitext, exists, basename
from abilities import AbilityGroups


if __name__ == "__main__":
    src_dir = abspath(join(dirname(__file__)))
    root_dir = abspath(join(src_dir, ".."))    
    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast = True)    
    build_dir = join(root_dir, "build")

    count = 0
    for ability_group in ability_groups:
        print(f"-- {ability_group.get_title()}")
        for ability in ability_group:
            problems = ability.get_problems()
            if len(problems) > 0:
                print('%s' % ability.get_title())
                print('\t' + '\n\t'.join(problems))
                print()

            count += 1
    print(f"Count: {count}")
