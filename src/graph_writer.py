#!/usr/bin/env python
"""

  Draws the ability hierarchy graph
  (Doesn't appear in any docs?)

  Candidate for removal?

"""
import sys
import re
from os.path import abspath, join, splitext, dirname, exists, basename
from graphviz import Digraph
from abilities import AbilityGroups


src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))
sys.path.append(src_dir)


def _get_ability_label_html(ability):
    return """
    <tr>
    <td bgcolor="white" align="center">
    <font color="black" point-size="13" face="arial">
    {ability_name}
    </font>
    </td>
    </tr>""".format(ability_name = ability.get_title())


def _get_ability_rank_html(ability_rank):
    return """
    <tr>
    <td align="right" port="{ability_rank_id}">
    <font color="black">
    {ability_rank}
    </font>
    </td>
    </tr>""".format(
        ability_rank = ability_rank.get_rank_number(),
        ability_rank_id = ability_rank.get_id(),
    )


def _get_ability_html(ability):

    html = "<<table>"
    html += _get_ability_label_html(ability)
    for ability_rank in ability.get_ranks():
        html += _get_ability_rank_html(ability_rank)
    html += "</table>>"    
    return html



        
def draw_skill_tree(build_dir, ability_groups):
        
    dot = Digraph(
        engine = "fdp",
        comment = "Ability Dependencies",
        node_attr={'shape': 'plaintext'},
    )

    # Fill an A4 sheet
    dot.graph_attr["size"] = "8.3,11.7!"
    dot.graph_attr["margin"] = "0.5"
    dot.graph_attr["ratio"] = "fill"
    edges = []

    # add the nodes
    for ability_group in ability_groups:        
        for ability in ability_group.get_abilities():            
            node_str = _get_ability_html(ability)
            node_str = re.sub(r'\s+', ' ', node_str)
            dot.node(ability.get_id(), node_str)

    # add the prereq arrows
    for ability_group in ability_groups:
        for ability in ability_group.get_abilities():            
            for ability_rank in ability.get_ranks():
                for prereq in ability_rank.get_prerequisites():
                    prereq_ability = prereq.get_ability()
                    if prereq_ability is None:
                        continue                    
                    prereq_id = prereq_ability.get_id() + ":" + prereq.get_id()
                    ability_rank_id = ability.get_id() + ":" + ability_rank.get_id()
                    edges.append((ability_rank_id, prereq_id))

    dot.edges(edges)                
    dot.render(join(build_dir, "abilities.gv"), view = True)
    return



if __name__ == "__main__":
    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir, fail_fast=True)
    build_dir = join(root_dir, "build")
    draw_skill_tree(build_dir, ability_groups)
