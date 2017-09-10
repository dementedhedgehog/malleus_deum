#!/usr/bin/env python
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


def _get_ability_level_html(ability_level):
    # return """
    # <tr>
    # <td bgcolor="white" align="right" colspan="2" port="{ability_level_id}">
    # <font color="black">
    # {ability_level_id} 
    # {ability_level}
    # </font>
    # </td>
    # </tr>""".format(
    return """
    <tr>
    <td align="right" port="{ability_level_id}">
    <font color="black">
    {ability_level}
    </font>
    </td>
    </tr>""".format(
        ability_level = ability_level.get_level_number(),
        ability_level_id = ability_level.get_id(),
    )


def _get_ability_html(ability):

    html = "<<table>"
    html += _get_ability_label_html(ability)
    for ability_level in ability.get_levels():
        html += _get_ability_level_html(ability_level)
    html += "</table>>"    
    return html



        
def draw_skill_tree(build_dir, ability_groups):
        
    dot = Digraph(
        #engine = "dot",
        #engine = "circo",
        #engine = "sfdp",
        engine = "fdp",
        #engine = "osage",
        #repulsiveforce = 2.0,
        comment = "Ability Dependencies",
        #node_attr={'shape': 'record'}
        node_attr={'shape': 'plaintext'},
    )

    #dot.graph_attr["repulsiveforce"] = "1.5"
    #dot.graph_attr["K"] = "2.0"

    # Fill an A4 sheet
    dot.graph_attr["size"] = "8.3,11.7!"
    dot.graph_attr["margin"] = "0.5"
    dot.graph_attr["ratio"] = "fill"

        # size="8.3,11.7!",
        # margin=0,

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
            for ability_level in ability.get_levels():
                for prereq in ability_level.get_prerequisites():
                    prereq_id = prereq.ability.get_id() + ":" + prereq.get_id()
                    ability_level_id = ability.get_id() + ":" + ability_level.get_id()
                    edges.append((ability_level_id, prereq_id))

    dot.edges(edges)
                
    dot.render(join(build_dir, "abilities.gv"), view = True)
    return



if __name__ == "__main__":

    ability_groups = AbilityGroups()
    ability_groups_dir = join(root_dir, "abilities")
    ability_groups.load(ability_groups_dir)    
    build_dir = join(root_dir, "build")
    draw_skill_tree(build_dir, ability_groups)
