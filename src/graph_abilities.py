#!/usr/bin/env python
"""

 Generate a graph of abilities.


"""
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
from graphviz import Digraph
from abilities import AbilityGroups

src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
build_dir = join(root_dir, "build")
build_graph = join(build_dir, "abilities.gv")
ability_groups_dir = join(root_dir, "abilities")


if __name__ == "__main__":

    dot = Digraph(comment='Abilities')
    dot.attr(rankdir="LR")
    dot.attr(autosize="false")
    dot.attr(size="25.7,8.3!")

    
    # with g.subgraph(name='inborn_1') as c:
    #     for ability_group in ability_groups:
    #         for ability in ability_group:

    #             print ability.get_title()
    #             records = []
    #             for ability_level in ability.get_levels():
    #                 records.append("<%s> %s" % (ability_level.get_id(),
    #                                             ability_level.get_title()))

    #             record_label = "|".join(records)
    #             dot.node(ability.get_id(),
    #                      record_label,
    #                      shape="record")

        
    
    ability_groups = AbilityGroups()
    if not ability_groups.load(ability_groups_dir, fail_fast=True):
        print "Errors parsing abilities.. failing fast!"
        sys.exit()
        
    for ability_group in ability_groups:
        for ability in ability_group:

            print ability.get_title()
            records = []
            for ability_level in ability.get_levels():
                records.append("<%s> %s" % (ability_level.get_id(),
                                            ability_level.get_title()))

            record_label = "|".join(records)
            dot.node(ability.get_id(),
                     record_label,
                     shape="record")

                
    for ability_group in ability_groups:
        for ability in ability_group:
            for ability_level in ability.get_levels():
                for ability_level_prereq in ability_level.get_ability_level_prereqs():
                    
                    from_record = '%s:%s' % (
                        ability_level_prereq.get_ability().get_id(),
                        ability_level_prereq.get_ability_level_id())

                    to_record = '%s:%s' % (
                        ability.get_id(),
                        ability_level.get_id())
                                            
                    dot.edge(from_record, to_record)

    dot.render(build_graph, view=True)
    #print dot.source
    dot.save()
