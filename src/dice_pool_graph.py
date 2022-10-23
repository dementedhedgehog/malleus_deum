#!/usr/bin/python3
"""
  New version counts the number of 6s

"""
import sys
import math
from os.path import join
from operator import add

from PIL import Image
import pygal
from pygal.style import DefaultStyle
import cairo


from utils import build_dir


n_sides = 6
dice_pool_range = range(1, 11)
MAX_GROUNDING_DIFF = 3
FONT_FAMILY = 'googlefont:Raleway'
FONT_SIZE = 22

from functools import lru_cache


class BarSegmentInfo:
    """
    Each bar in our bar graphs can be composed of 
    multiple segments.  This class holds that segment
    information.

    """    
    def __init__(self, title, colour):
        # segment legend text
        self.title = title

        # rgb 0-255 triple
        self.colour = colour

    def get_cairo_colour(self):
        return self.colour[0]/255.0, self.colour[1]/255.0, self.colour[2]/255.0

    def get_pygal_colour(self):
        return pygal.colors.unparse_color(
            self.colour[0],
            self.colour[1],
            self.colour[2],
            0.0,
            "#rrggbb")

# colour map colour scheme from here.
# https://colorbrewer2.org/?type=sequential&scheme=PuBuGn&n=5
# failed is not in the colourmap.. basically the colourmap is
# sequential except for failed which is in its own "qualitative space"
failed_seg = BarSegmentInfo("Failed", (189,0,38))

bar_segments = [
    # different degrees of success
    BarSegmentInfo("Succeeded",  (4,90,141)),
    BarSegmentInfo("Overcharge 1", (43,140,190)),
    BarSegmentInfo("Overcharge 2", (116,169,207)),
    BarSegmentInfo("Overcharge 3", (166,189,219)),
    BarSegmentInfo("Overcharge 4", (208,209,230)),
    BarSegmentInfo("Overcharge 5", (241,238,246)),
]


def get_probs(dice_probs, idx):
    try:
        return dice_probs[idx]
    except IndexError:        
        return 0.0


@lru_cache()
def factorial(n):
    """
    Calculate the factorial of an input using memoization
    :param n: int
    :rtype value: int
    """
    assert n >= 0
    return 1 if (n in (0, 1)) else (n * factorial(n-1))


@lru_cache()
def C(n, k):
    """Choose k elements from a set of n elements."""
    return 0 if k > n else factorial(n) // (factorial(k) * factorial(n-k))


def combos_sum_total(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total with n_dice each with n_sides.

    """       
    combos = 0
    for i in range(0, n_dice+1):
        combos += pow(-1, i) * C(n_dice, i) * C(total - i*n_sides - 1, n_dice - 1)
    return combos


def get_combos_lt(total, n_dice, n_sides=6):
    """Return the number of ways of rolling less than total with n_dice each with n_sides."""
    from_total = n_dice
    combos = 0
    for t in range(from_total, total):
        combos += combos_sum_total(t, n_dice, n_sides)
    return combos


@lru_cache()
def get_probs_lt(total, n_dice):
    """Returns the probability of rolling with the sum of n_dice < total."""
    return get_combos_lt(total, n_dice) / get_total_combos(n_dice)


def get_combos(total, n_dice):
    """
    Returns a list containing the number of combos to get total with 
    n_dice with [0_sixes, 1_six, 2_sixes, etc .. ]

    """
    max_sixes = min(total // 6, n_dice)
    combos = []
    for n6s in range(0, max_sixes+1):
        new_total = total - n6s*6
        new_dice = n_dice - n6s
        if new_dice == 0:
            continue
        if new_total == 6 and new_dice == 1:
            combos.append(0)
            combos.append(1)
        else:
            c = combos_sum_total(new_total, new_dice, 5) * C(n_dice, new_dice)
            combos.append(c)    
    return combos


def get_combos_geq(total, n_dice):
    """
    Get the combos of dice from n_dice that add up to total 
    broken down by the number of 6s used.

    """
    totals = [0] * (n_dice+1)
    max_total = 6 * n_dice
    for t in range(total, max_total+1):
        new_totals = get_combos(t, n_dice)
        for i in range(len(new_totals)):
            totals[i] += new_totals[i]
    return totals


@lru_cache()
def get_total_combos(n_dice):
    """Return the total number of combinations possible with n d6."""
    return float(pow(6, n_dice))


@lru_cache()
def get_probs_geq(total, n_dice):
    """Returns a list of probabilities of having the sum of n_dice >= total."""
    totals = get_combos_geq(total, n_dice)
    probs = []
    for i in range(len(totals)):
        probs.append(totals[i] / get_total_combos(n_dice))
    return probs


class GraphValue:
    
    def __init__(self, value, label):
        self.value = value
        self.label = label

    def __lt__(self, other):
        return self.value < other
    
    def __isub__(self, other):
        self.value = self.value - other
        return self.value

    def __iadd__(self, other):
        self.value = self.value + other
        return self.value

    def __ge__(self, other):
        return self.value >= other

    def __radd__(self, other):
        return self.value + other

    def __str__(self):
        return f"{self.label} {(100 * self.value):.0f}"

    def __int__(self):
        return self.value


def prob_of_n6s(n_dice, min_prob=None):
    total = float(pow(6, n_dice))
    probs = []
    for number_of_d6s in range(0, n_dice+1):
        n_not_6 = n_dice - number_of_d6s
        count = comb(n_dice, n_not_6) * pow(5, n_not_6)
        prob = 100.0 * count/total
        if min_prob is not None and prob < min_prob:
            break
        probs.append(prob)        
    return probs
    

def graph_dc(fname, difficulty):
    """
    Draw a graph for one dc (with various numbers of 6s).

    """
    line_chart = pygal.StackedBar(
        print_values=True,
        show_legend=False,
        show_y_guides=False,
        show_y_labels=False,
        y_axis=False,
        style=DefaultStyle(
            value_font_family=FONT_FAMILY,
            value_font_size=FONT_SIZE,
            title_font_size = 30,
        ))

    # x axis is Number of Dice Rolled.
    # y axis is Probability
    line_chart.value_formatter = lambda x: str(x) if x >= 0.04 else ""
    line_chart.title = f'DC:{difficulty}'
    line_chart.x_labels = [str(x) for x in dice_pool_range]

    # check if the lower difficulty always succeeds?  If so we can stop.
    min_d = 0
    max_d = max(dice_pool_range)

    # This is for the successful rolls
    dice_probs = {}
    fail_probs = {}
    for n_dice in dice_pool_range:
        probs =  get_probs_geq(difficulty, n_dice)
        dice_probs[n_dice] = probs

        # This is the unsuccessful rolls    
        fail_probs[n_dice] = get_probs_lt(difficulty, n_dice)

    # Failure!
    values = []
    for d in dice_pool_range:
        if d < min_d or d > max_d:
            values.append({})
        else:
            c = failed_seg.get_pygal_colour()
            values.append(
                {
                    'value': GraphValue(
                        fail_probs[d],
                    ""),
                    'style': f'fill: {c}; stroke: black; stroke-width: 2',
                })       
    line_chart.add(failed_seg.title, values)

    # Successes .. one bar segment per "number of sixes rolled"
    for seg_num, seg in enumerate(bar_segments):
        values = []
        for d in dice_pool_range:
            if d < min_d or d > max_d:
                values.append({})
            else:
                c = seg.get_pygal_colour()
                values.append(
                    {
                        'value': GraphValue(
                            get_probs(dice_probs[d], seg_num),
                            ""),
                        'style': f'fill: {c}; stroke: black; stroke-width: 2',
                    })       
        line_chart.add(seg.title, values)
    line_chart.render_to_png(fname)

    
def generate_legend(fname, width, height):
    """Draw the legend for the combined graph."""

    # Make a context with dimensions scaled from 0.0 to 1.0
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)
    ctx.scale(width, height)  
    
    # Paint the background white.
    pat = cairo.SolidPattern(1.0, 1.0, 1.0, 1.0)
    ctx.rectangle(0, 0, 1, 1)
    ctx.set_source(pat)
    ctx.fill()

    # Change the current transformation matrix (add a border)
    ctx.translate(0.1, 0.1)

    # approximate text height
    ctx.select_font_face(FONT_FAMILY, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)


    
    # layout the legend
    x = 0.0
    y = 0.05
    y_step = 0.08
    square_dimension = 0.08
    _, _, _, text_height, _, _ = ctx.text_extents("lg")
    text_x_offset = 0.05
    text_y_offset = y

    # Legend title
    ctx.set_font_size(0.06)
    ctx.set_source_rgb(0, 0, 0) 
    ctx.move_to(0, 0)      
    ctx.show_text("Legend")
    ctx.stroke()
    
    # swatches
    ctx.set_font_size(0.04)
    for segment in [failed_seg, ] + bar_segments:
        
        # draw segment color swatch
        colour = segment.get_cairo_colour()
        ctx.set_source_rgb(*colour)        
        ctx.rectangle(x, y, x+square_dimension, y+square_dimension)
        ctx.fill()

        # draw legend label
        ctx.set_source_rgb(0, 0, 0) 
        ctx.move_to(x + square_dimension + text_x_offset, y + text_y_offset)      
        ctx.show_text(segment.title)
        ctx.stroke()

        # next line
        y += y_step

    # draw explanatory text
    for line in ("X axis is number of d6 rolled.", "Y axis is percent chance."):
        ctx.set_source_rgb(0, 0, 0) 
        ctx.move_to(0, y + text_y_offset)      
        ctx.show_text(line)
        y += y_step

    surface.write_to_png(fname)
    
    
    
def generate_oc_dice_pool_graph(from_dc, to_dc, out_fname):
    """
    A dice pool graph is a composite of other graphs.

    """
    fnames = []

    # write out a bunch of little graphs, one per dc.
    for dc in range(from_dc, to_dc+1):
        fname = join(build_dir, f'oc_pool_{dc}.png')
        graph_dc(fname, dc)
        fnames.append(fname)

    # now load those images 
    imgs = []
    for img_fname in fnames:
        img = Image.open(img_fname)
        imgs.append(img)

    # create a legend image the same size as the other graphs
    first_img = imgs[0]
    width, height = first_img.size
    legend_fname = join(build_dir, 'oc_pool_legend.png')
    generate_legend(legend_fname, width, height)
    img = Image.open(legend_fname)
    imgs.append(img)
        
    # arrange the per-dc-graph imgs into rows of 3
    step = 3
    max_imgs = len(imgs)
    img_rows = [imgs[i:i+step] for i in range(0, max_imgs, step)]
    row_widths = []
    row_heights = []
    for img_row in img_rows:
        widths, heights = zip(*(i.size for i in img_row))
        total_width = sum(widths)
        max_height = max(heights)
        row_widths.append(total_width)
        row_heights.append(max_height)

    # work out the dimensions of the combined rows
    width = max(row_widths)
    height = sum(row_heights)
    new_img = Image.new('RGB', (width, height))

    # draw all the images
    x_offset = 0
    y_offset = 0
    row_number = 0
    y = 0
    for img_row in img_rows:
        x_offset = 0
        for img in img_row:
            new_img.paste(img, (x_offset, y_offset))
            x_offset += img.size[0]
        y_offset += row_heights[row_number]    
        row_number += 1
    new_img.save(out_fname)
    return



def build_dice_pool_graphs(): 
    out_fname="./frog.png"

    for from_dc, to_dc in ((1, 14), (15, 28)):
        fname = join(build_dir, f'dice_pool_{from_dc}_to_{to_dc}.png')    
        generate_oc_dice_pool_graph(from_dc, to_dc, out_fname=fname)

    
if __name__ == "__main__":
    build_dice_pool_graphs()
