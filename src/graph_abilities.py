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



#def find_group(ability_lookup, ability)


class Groups:

    def __init__(self):
        self.groups = []
        self.abilities = set()
        return

    def __str__(self):

        str_rep = ""
        for group in self.groups:
            str_rep += ("(" +
                        ", ".join([ability.get_id() for ability in group]) +
                        ")\n\n")
        return str_rep


    def walk_ability_dependencies(self, ability, group = None):

        # Check if the ability is in the lookup table.
        if ability in self.abilities:
            return
        self.abilities.add(ability)

        # Add ourselves to a group.
        if group is None:
            group = set()
            self.groups.append(group)
        group.add(ability)

        # get a set of prereq abilities for this ability.
        for ability_level in ability.get_levels():
            prereq_ability_levels = ability_level.get_ability_level_prereqs()
            for prereq_ability_level in prereq_ability_levels:
                prereq = prereq_ability_level.get_ability()
                self.walk_ability_dependencies(prereq, group)

        # now also find the dependencies
        for ability_level in ability.get_levels():
            for dependency_ability_level in ability_level.get_dependencies():
                dependency = dependency_ability_level.get_ability()
                #group.add(dependency)
                self.walk_ability_dependencies(dependency, group)
        return






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


    # map ability id to the set of abilities they're connected to.
    #ability_lookup = defaultdict(set)
    groups = Groups()

    
    ability_groups = AbilityGroups()
    if not ability_groups.load(ability_groups_dir, fail_fast=True):
        print "Errors parsing abilities.. failing fast!"
        sys.exit()
        
    for ability_group in ability_groups:
        for ability in ability_group:
            groups.walk_ability_dependencies(ability)


    print "-----"
    print groups

    #sys.exit()
    i = 0
    for group in groups.groups:

        subgraph_name = "subgraph_%s" % i
        i += 1
        print "-----------------------------_"
        print subgraph_name
        
        with dot.subgraph(name=subgraph_name) as s:
            #for ability_group in ability_groups:
            for ability in group:

                print ability.get_title()
                records = []
                for ability_level in ability.get_levels():
                    records.append("<%s> %s" % (ability_level.get_id(),
                                                ability_level.get_title()))

                record_label = "|".join(records)
                s.node(ability.get_id(),
                       record_label,
                       shape="record")

            for ability in group:
                for ability_level in ability.get_levels():
                    for ability_level_prereq in ability_level.get_ability_level_prereqs():

                        from_record = '%s:%s' % (
                            ability_level_prereq.get_ability().get_id(),
                            ability_level_prereq.get_ability_level_id())

                        to_record = '%s:%s' % (
                            ability.get_id(),
                            ability_level.get_id())

                        s.edge(from_record, to_record)
                    
    
    # ability_groups = AbilityGroups()
    # if not ability_groups.load(ability_groups_dir, fail_fast=True):
    #     print "Errors parsing abilities.. failing fast!"
    #     sys.exit()
        
    # for ability_group in ability_groups:
    #     for ability in ability_group:

    #         print ability.get_title()
    #         records = []
    #         for ability_level in ability.get_levels():
    #             records.append("<%s> %s" % (ability_level.get_id(),
    #                                         ability_level.get_title()))

    #         record_label = "|".join(records)
    #         dot.node(ability.get_id(),
    #                  record_label,
    #                  shape="record")

                
    # for ability_group in ability_groups:
    #     for ability in ability_group:
    #         for ability_level in ability.get_levels():
    #             for ability_level_prereq in ability_level.get_ability_level_prereqs():
                    
    #                 from_record = '%s:%s' % (
    #                     ability_level_prereq.get_ability().get_id(),
    #                     ability_level_prereq.get_ability_level_id())

    #                 to_record = '%s:%s' % (
    #                     ability.get_id(),
    #                     ability_level.get_id())
                                            
    #                 dot.edge(from_record, to_record)

    dot.render(build_graph, view=True)
    #print dot.source
    dot.save()
