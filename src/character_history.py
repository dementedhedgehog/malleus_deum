#!/usr/bin/python3
"""

  Draws Trees.   


"""
import sys
import utils
import cairo
import math
from copy import copy
from os.path import abspath, join, splitext, dirname, exists, basename

import draw
from utils import parse_xml, validate_xml, COMMENT

WIDTH = 296
HEIGHT = 400 # This is the initial height, image will be scaled to fit
FONT_SIZE = 8

MARGIN_TOP = 4
MARGIN_LEFT = 4
MARGIN_RIGHT = 4
MARGIN_BOTTOM = 4
CIRCLE_RADIUS = 4
CIRCLE_HORIZONTAL_SEPARATOR = 2
LEVEL_SEPARATOR = CIRCLE_RADIUS + 2



class HistoryNode:

    def __init__(self, name=None, parent=None, spline=[]):
        # width of the node (used for relative layout)
        self.width = None
        self.height = None
        self.children = []

        self.name = name
        #self.spline = spline
        self.parent = parent

        #self._id = None
        #self.name = None
        #self.spline = None    
        
        if parent is not None:            
            parent.children.append(self)

        # where outgoing splines should start from
        self.outgoing_connection_point = None


    def calc_size(self, context):
        """
        Calculates the width of the node.  We need to know
        all the node widths before we can layout anything.

        """
        # get the text size
        (xt, yt, width, height, dx, dy) = context.text_extents(self.name)

        # width of the whole ability node.
        self.width = width
        self.height = height
        return

    def draw(self, context, starting_pos):
        x, y = starting_pos

        (xt, yt, width, height, dx, dy) = context.text_extents(self.name)
        half_width = width / 2
        half_height = height / 2

        # work out the bounds of the nodes rectangle
        x0, y0 = (x - half_width - MARGIN_LEFT, y)
        x1, y1 = (x + half_width + MARGIN_RIGHT, y + half_height + MARGIN_TOP + MARGIN_BOTTOM)
        
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
        context.move_to(x0 + MARGIN_LEFT, y0 + half_height + MARGIN_TOP)
        context.show_text(self.name)
        
        # draw the little ball on middle top that represents the incoming pos.
        black_ball_radius = 2
        black_ball_vertical_offset = -1
        context.arc(x, y, black_ball_radius, 0, black_ball_radius*math.pi)
        context.fill()
        
        max_y = y1 + MARGIN_BOTTOM
        self.outgoing_connection_point = (x, max_y)
        return starting_pos, max_y


    def load(self, node):
        for child in list(node):
           tag = child.tag
           # if tag == "id":
           #     if self._id is not None:
           #         raise Exception("Only one id per history node. (%s) %s\n" %
           #                         (child.tag, str(child)))
           #     else:
           #         # save the id location for debugging (can't have duplicates)!
           #         self._id = child.text

           #el
           if tag == "name":
               if self.name is not None:
                   raise Exception("Only one name per history node. (%s) %s\n" %
                                   (child.tag, str(child)))
               else:
                   # save the id location for debugging (can't have duplicates)!
                   self.name = child.text

           elif tag == "spline":
               self.spline = parse_spline(child.getchildren())

           elif tag == "node":
               node = HistoryNode(parent=self)
               node.load(child)
               self.children.append(node)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
    


def get_root_nodes(nodes):
    roots = copy(nodes)
    for node in nodes:
        for child in node.children:
            if child in roots:
                roots.remove(child)
    return roots


def layout(node, nodes, context, offset=None, max_y=0):
    
    # calculate position of the spline points and ability node
    if offset is None:
        spline_points = [(WIDTH/2, MARGIN_TOP), ] + node.spline 
        offset_spline_points = spline_points
        starting_pos = draw.add_spline_points(offset_spline_points)
    else:
        spline_points = [(0, 0), ] + node.spline 
        #spline_points = [node.parent.outgoing_connection_point, ] + node.spline 
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
    x, y = starting_pos
    for child in node.children:
        try:            
            child_pos = x, y + 2*CIRCLE_RADIUS + CIRCLE_HORIZONTAL_SEPARATOR
            new_max_y = layout(child, nodes, context, offset=child_pos, max_y=max_y)
            max_y = max(max_y, new_max_y)
        except KeyError:
            pass
    return max_y


def draw_tree(nodes, fname, height=HEIGHT):
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
    
    # calculate the nodes size
    for node in nodes:
        node.calc_size(context)
    
    # draw the ability tree
    roots = get_root_nodes(nodes)
    max_y = 0
    for root in roots:
        new_max_y = layout(root, nodes, context)
        max_y = max(new_max_y, max_y)

    # draw a frame
    draw_frame = False
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


def parse_spline(point_nodes):
    points = []
    for point_node in point_nodes:
        x = float(point_node.attrib["x"])
        y = float(point_node.attrib["y"])
        points.append((x, y))
    return points
        

class CharacterHistory:

    def __init__(self):
        self.nodes = []        

    def load(self, fname):
        f = open(fname)
        self.fname = fname 
        self.doc = parse_xml(fname)
        if self.doc is None:
            # failed to parse
            raise Exception(f"Failed to parse {fname}!!")

        # err_msg = validate_xml(self.doc)
        # if not err_msg is None:
        #     raise Exception(f"Fatal: xml errors are fatal! {err_msg}")
        
        root = self.doc.getroot()

        # check it's the right sort of element
        if root.tag != "characterhistory":
            raise Exception("UNKNOWN (%s) %s\n" % (root.tag, str(root)))
        
        # handle all the children of the character history
        for child in list(root):
           tag = child.tag
           if tag == "node":
               node = HistoryNode()
               node.load(child)
               self.nodes.append(node)

           elif tag is COMMENT:               
               pass # ignore comments!

           else:
               raise Exception("UNKNOWN (%s) %s\n" % (child.tag, str(child)))
        return


    def build_tree(self):
        fname = join(utils.build_dir, "XXXX_history_tree.eps")

        # We have to do this twice. Once to calculate the size and
        # once to draw in the new size.
        max_y = draw_tree(self.nodes, fname=fname)
        draw_tree(self.nodes, fname=fname, height=max_y)
        return

        
        
# def build_tree(history_nodes):
#     fname = join(utils.build_dir, "XXXX_history_tree.eps")

#     # We have to do this twice. Once to calculate the size and
#     # once to draw in the new size.
#     max_y = draw_tree(history_nodes, fname=fname)
#     draw_tree(history_nodes, fname=fname, height=max_y)
#     return


if __name__ == "__main__":
    # load the abilities
    #abilities_dir = join(root_dir, "abilities")
    #ability_groups = AbilityGroups()
    #ability_groups.load(abilities_dir, fail_fast=True)#


    history = CharacterHistory()
    history.load("dwarven_shield_warrior_history.xml")
    history.build_tree()

    # h1 = Node("frog")
    # h2 = Node("dog", parent=h1, spline=[(20, 20), ]) # (30, 30), (10, 10)])
    # h2 = Node("log", parent=h1, spline=[(-20, 20), ]) # (30, 30), (10, 10)])
    # #h1.children.append(h2)
    # build_tree([h1, h2])
    #h2 = HistoryNode("dog")
    #build_tree([h1, ])

    
