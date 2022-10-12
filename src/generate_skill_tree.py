#!/usr/bin/python3
"""

  Draws Skill/Ability Trees.   
   - these are the eps diagrams that should skill prereqs

"""
import sys
from os.path import abspath, join, splitext, dirname, exists, basename
import math
import cairo
from abilities import AbilityGroups
from utils import build_dir
import draw

src_dir = abspath(join(dirname(__file__)))
root_dir = abspath(join(src_dir, ".."))

WIDTH = 296
HEIGHT = 400 # This is the initial height, image will be scaled to fit
FONT_SIZE = 8

ABILITY_MARGIN_TOP = 4
ABILITY_MARGIN_LEFT = 4
ABILITY_MARGIN_RIGHT = 4
ABILITY_MARGIN_BOTTOM = 4
CIRCLE_RADIUS = 4
CIRCLE_HORIZONTAL_SEPARATOR = 2
ABILITY_RANK_SEPARATOR = CIRCLE_RADIUS + 2


class AbilityNode:
    """
    Graphic representation of an ability.

    """
    def __init__(self, ability):
        self.ability = ability

        # width of the node (used for relative layout)
        self.width = None
        self.height = None

        # map of ability_rank_id -> arrow connection position *relative* to
        # the incoming connection position of this node.
        self.outgoing_connector_offsets = {}        
        return

    def calc_size(self, context):
        """
        Calculates the width of the ability node.  We need to know
        all the node widths before we can layout anything.

        """
        # get the text size
        title = self.ability.get_title()
        (xt, yt, width, height, dx, dy) = context.text_extents(title)

        # width of the whole ability node.
        self.width = width
        self.height = height
        return

    def draw(self, context, starting_pos):
        x, y = starting_pos

        title = self.ability.get_title()
        (xt, yt, width, height, dx, dy) = context.text_extents(title)
        half_width = width / 2
        half_height = height / 2

        # work out the bounds of the nodes rectangle
        x0, y0 = (x - half_width - ABILITY_MARGIN_LEFT, y)
        x1, y1 = (x + half_width + ABILITY_MARGIN_RIGHT,
                  y + half_height + ABILITY_MARGIN_TOP + ABILITY_MARGIN_BOTTOM)
        
        # draw box
        context.move_to(x0, y0)
        context.line_to(x1, y0)
        context.line_to(x1, y1)
        context.line_to(x0, y1)
        context.line_to(x0, y0)
        context.stroke_preserve()        
        context.set_source_rgb(1, 1, 1)
        context.fill()
        context.set_source_rgb(0, 0, 0)

        # draw ability label
        context.move_to(x0 + ABILITY_MARGIN_LEFT, y0 + half_height + ABILITY_MARGIN_TOP)
        context.show_text(title)
        
        # draw the little ball on middle top that represents the incoming pos.
        black_ball_radius = 2
        black_ball_vertical_offset = -1
        context.arc(x, y, black_ball_radius, 0, black_ball_radius*math.pi)        
        context.fill()

        # draw the ability ranks.
        rank_x = x0 + ABILITY_RANK_SEPARATOR
        rank_y = y1 + ABILITY_MARGIN_TOP + CIRCLE_RADIUS
        for rank in self.ability.get_ranks():
            number = rank.get_rank_number()
            number_str = str(number)
            (xt, yt, width, height, dx, dy) = context.text_extents(number_str)
            context.move_to(rank_x - dx/2 + width/2, rank_y)
            
            # draw outgoing circle
            context.arc(rank_x, rank_y, CIRCLE_RADIUS, 0, 2.0*math.pi)
            context.stroke_preserve()        
            context.set_source_rgb(1, 1, 1)
            context.fill()
            context.set_source_rgb(0, 0, 0)

            # draw outgoing rank number
            context.move_to(rank_x - dx/2, rank_y + height/2)
            context.show_text(number_str)
            context.stroke()

            # remember where to connect to            
            self.outgoing_connector_offsets[number] = (rank_x, rank_y + CIRCLE_RADIUS)
            rank_x += 2 * CIRCLE_RADIUS + CIRCLE_HORIZONTAL_SEPARATOR

        if len(self.ability.get_ranks()) > 0:
            max_y = rank_y + CIRCLE_RADIUS
        else:
            max_y = y1
        max_y += ABILITY_MARGIN_BOTTOM
            
        return starting_pos, max_y

    def get_outgoing_offset(self, rank_number):
        return self.outgoing_connector_offsets[rank_number]


def draw_skill_tree(ability_groups, ability_group, ability, context, offset=None, max_y=0):
    """
    Lays out and draws the skill tree on the given context.

    """
    assert ability is not None
    node = AbilityNode(ability)

    # calculate the nodes size    
    node.calc_size(context)
    
    # calculate position of the spline points and ability node
    if offset is None:
        spline_points = [(WIDTH/2, ABILITY_MARGIN_TOP), ] + ability.spline 
        offset_spline_points = spline_points
        starting_pos = draw.add_spline_points(offset_spline_points)
    else:
        spline_points = [(0, 0), ] + ability.spline 
        offset_spline_points = draw.calc_spline_offsets(offset, spline_points)
        starting_pos = offset_spline_points[-1]
    
    # calculate the nodes offset.
    starting_pos, new_max_y = node.draw(context, starting_pos)
    max_y = max(max_y, new_max_y)
    draw.draw_square(context, *starting_pos)
    
    # draw the spline if any
    if offset is not None:
        draw.draw_spline(context, offset_spline_points)

    # first set all the offsets
    children = ability_groups.get_abilities_children(ability)
    if children is not None:
       for child_ability in children:
           prereq_ability_rank = child_ability.ability_rank_prereq

           if prereq_ability_rank is not None:
               ability_rank_number = prereq_ability_rank.get_rank_number()
               assert isinstance(ability_rank_number, int)
           else:
               ability_rank_number = 0

           try:
               child_pos = node.get_outgoing_offset(ability_rank_number)
               new_max_y = draw_skill_tree(ability_groups, ability_group, child_ability,
                                           context, offset=child_pos, max_y=max_y)
               max_y = max(max_y, new_max_y)
           except KeyError:
               pass
    return max_y


def _build_skill_tree(ability_groups, ability_group, fname, height=HEIGHT, draw_frame=False):

    # set up cairo surface
    _, ext = splitext(fname)
    if ext == ".eps":
        surface = cairo.PSSurface(fname, WIDTH, height)
        surface.set_eps(True)
    elif ext == ".svg":
        surface = cairo.SVGSurface(fname, WIDTH, height)
    elif ext == ".pdf":
        surface = cairo.PDFSurface(fname, WIDTH, height)
    else:
        raise Exception("Unknown ability tree image type: %s" % ext)

    # set up cairo context
    context = cairo.Context(surface)
    context.set_source_rgba(0, 0, 0, 1.0)
    context.set_line_width(1)
    context.set_line_cap(cairo.LINE_CAP_ROUND)
    context.set_line_join(cairo.LINE_JOIN_ROUND)

    # paint background
    context.set_source_rgba(1.0, 1.0, 1.0, 1.0)
    context.rectangle(0, 0, WIDTH, height)
    context.fill()    

    # setup font
    context.select_font_face("Verdana",
                             cairo.FONT_SLANT_NORMAL,
                             cairo.FONT_WEIGHT_NORMAL)
    context.set_font_size(FONT_SIZE)
    context.set_source_rgb(0, 0, 0)

    # draw the ability tree
    root_abilities = ability_group.get_root_abilities()
    max_y = 0
    for ability in root_abilities:
        new_max_y = draw_skill_tree(ability_groups, ability_group, ability, context)
        max_y = max(new_max_y, max_y)

    # draw a frame
    if draw_frame:
        FRAME_LINE_WIDTH = 1
        context.set_line_width(FRAME_LINE_WIDTH)
        context.set_source_rgb(0, 0, 0)    
        context.move_to(0, 0)
        context.line_to(WIDTH - FRAME_LINE_WIDTH, 0)
        context.line_to(WIDTH - FRAME_LINE_WIDTH, max_y - FRAME_LINE_WIDTH)
        context.line_to(0, max_y - FRAME_LINE_WIDTH)
        context.line_to(0, 0)
        context.stroke_preserve()

    # clip the drawing to the drawing size
    context.rectangle(0, 0, WIDTH, math.ceil(max_y))
    context.clip()

    # .. and we're done.
    surface.finish()
    return max_y


def build_skill_trees(ability_groups):
    for ability_group in ability_groups: 
        ability_group_id = ability_group.info.ability_group_id
        fname = join(build_dir, ability_group_id + "_skill_tree.eps")
        
        # The root ability has the same name as the ability group.
        max_y = _build_skill_tree(ability_groups, ability_group, fname=fname)
        _build_skill_tree(ability_groups, ability_group, fname=fname, height=max_y)
        
    
if __name__ == "__main__":
    # load the abilities
    abilities_dir = join(root_dir, "abilities")
    ability_groups = AbilityGroups()
    ability_groups.load(abilities_dir, fail_fast=True)

    build_skill_trees(ability_groups)

