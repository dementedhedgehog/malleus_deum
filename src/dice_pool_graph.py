#!/usr/bin/python3
import sys
from os.path import join

from PIL import Image
import pygal
from pygal.style import DefaultStyle

from utils import build_dir


n_sides = 6
dice_pool_range = range(1, 11)
MAX_GROUNDING_DIFF = 3


from functools import lru_cache


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


def combos_sum_total_or_more(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total or more with n_dice each with n_sides.

    """
    max_total = n_dice * n_sides
    from_total = min(total, max_total + 1)
    combos = 0
    for t in range(from_total, max_total + 1):
        combos += combos_sum_total(t, n_dice, n_sides)
    return combos


def combos_sum_total_or_less(total, n_dice, n_sides):
    """
    Return the number of ways of rolling total or less with n_dice each with n_sides.

    """
    max_total = n_dice * n_sides
    from_total = n_dice
    to_total = min(total, max_total)

    combos = 0
    for t in range(from_total, to_total + 1):
        combos += combos_sum_total(t, n_dice, n_sides)
    return combos


def prob_sum_total(total, n_dice, n_sides):
    """
    Return the chance of rolling exactly total with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total(total, n_dice, n_sides) / float(total_combos)


def prob_sum_total_or_more(total, n_dice, n_sides):
    """
    Return the chance of rolling total or more with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total_or_more(total, n_dice, n_sides) / float(total_combos)


def prob_sum_total_or_less(total, n_dice, n_sides):
    """
    Return the chance of rolling total or less with n_dice having n_sides.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total_or_less(total, n_dice, n_sides) / float(total_combos)


def prob_sum_total_or_less_min(total, n_dice, n_sides, choose_n_min):
    """
    Return the chance of rolling total or less with n_dice having n_sides.
    Discarding the top n_dice - choose_n_min dice.

    """
    total_combos = pow(n_sides, n_dice)
    return combos_sum_total_or_less(total, n_dice, n_sides) / float(total_combos)



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
        return f"{self.label} {(100 * self.value):.0f}%"

    def __int__(self):
        return self.value


    

def create_img(fname, difficulty, overcharge, show_legend=False):
    """
    Overcharge is the DC + diff, not just the diff.

    """
    line_chart = pygal.StackedBar(
        print_values=True,
        show_legend=show_legend,
        show_y_guides=False,
        show_y_labels=False,
        y_axis=False,
        legend_at_bottom=True,
        style=DefaultStyle(
            value_font_family='googlefont:Raleway',
            value_font_size=15,
        ))

    # x axis is Number of Dice Rolled.
    # y axis is Probability
    line_chart.value_formatter = lambda x: str(x) if x >= 0.04 else ""
    line_chart.title = f'DC:{difficulty} with Overcharge:{overcharge}'
    line_chart.x_labels = [str(x) for x in dice_pool_range]
    overcharge_with_grounding = overcharge + MAX_GROUNDING_DIFF

    # check if the lower difficulty always succeeds?  If so we can stop.
    #cutoff_d = max(dice_pool_range)
    min_d = 0
    max_d = max(dice_pool_range)
    for n_dice in dice_pool_range:
        p_min = prob_sum_total_or_less(difficulty-1, n_dice, n_sides)
        if p_min < 0.99:
            min_d = n_dice
            break

    for n_dice in dice_pool_range:
        # probability we roll under the difficulty?
        p_max = prob_sum_total_or_less(difficulty-1, n_dice, n_sides)
        if p_max < 0.01:
            max_d = n_dice
            break
    values = []
    for d in dice_pool_range:
        if d < min_d or d > max_d:
            values.append({})
        else:
            values.append(
                {
                    'value': GraphValue(
                        prob_sum_total_or_less(difficulty-1, d, n_sides),
                        ""),
                    'style': 'fill: yellow; stroke: black; stroke-width: 2',
                })       
    line_chart.add("Under", values)


    values = []
    for d in dice_pool_range:
        if d < min_d or d > max_d:
            values.append({})
        else:
            values.append(
                {
                    'value': GraphValue(
                    (prob_sum_total_or_less(overcharge+1, d, n_sides) -
                     prob_sum_total_or_less(difficulty-1, d, n_sides)),
                    ""),
                    'style': 'fill: green; stroke: black; stroke-width: 2',
                })    
    line_chart.add("OK", values)

    values = []
    for d in dice_pool_range:
        if d < min_d or d > max_d:
            values.append({})
        else:
            values.append(
                {
                "value": GraphValue(
                    prob_sum_total_or_less(overcharge_with_grounding, d, n_sides) -
                    prob_sum_total_or_less(overcharge + 1, d, n_sides),
                    ""),
                'style': 'fill: orange; stroke: black; stroke-width: 2'
                })  
    line_chart.add("Ground", values)

    # 
    values = []
    for d in dice_pool_range:
        if d < min_d or d > max_d:
            values.append({})
        else:
            values.append(
                {
                'value': GraphValue(
                    prob_sum_total_or_more(overcharge_with_grounding+1, d, n_sides),
                    ""),
                'style': 'fill: transparent; stroke: black; stroke-width: 2'
                })    
    line_chart.add("Overcharge", values)

    line_chart.render_to_png(fname)


    
def generate_dice_pool_graph(dc_ocs, out_fname):
    fnames = []
    first_img = True
    for difficulty, overcharge in dc_ocs:        
        fname = join(build_dir, f'dice_pool_{difficulty}_{overcharge}.png')
        create_img(fname, difficulty, overcharge, show_legend=False)
        fnames.append(fname)
        first_img = False

    imgs = []
    for img_fname in fnames:
        img = Image.open(img_fname)
        imgs.append(img)

    # Sort the imgs into rows of 3
    step = 3
    max_imgs = len(imgs) - (len(imgs) % step)
    img_rows = [imgs[i:i+step] for i in range(0, max_imgs, step)]

    row_widths = []
    row_heights = []
    for img_row in img_rows:
        widths, heights = zip(*(i.size for i in img_row))
        total_width = sum(widths)
        max_height = max(heights)
        row_widths.append(total_width)
        row_heights.append(max_height)

    width = max(row_widths)
    height = sum(row_heights)
    new_img = Image.new('RGB', (width, height))

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


def generate_dice_pool_graphs():
    out_fname = join(build_dir, f'dice_pools_d{n_sides}_a.png')
    dc_ocs = (
            (2, 6), (2, 9),  (2, 12), 
            (3, 10), (3, 14), (3, 18), 
            (4, 10), (4, 14), (4, 18), 
            (5, 10), (5, 14), (5, 18), 
            (6, 10), (6, 14), (6, 18),
            (7, 14), (7, 17), (7, 21), 
    )    
    generate_dice_pool_graph(dc_ocs=dc_ocs, out_fname=out_fname)
    
    out_fname = join(build_dir, f'dice_pools_d{n_sides}_b.png')
    dc_ocs = (
            (8, 18), (8, 20), (8, 26), 
            (9, 18), (9, 20), (9, 26), 
            (10, 22), (10, 24), (10, 28), 
            (11, 22), (11, 24), (11, 28), 
            (12, 22), (12, 24), (12, 28), 
            (13, 22), (13, 24), (13, 28), 
    )
    generate_dice_pool_graph(dc_ocs=dc_ocs, out_fname=out_fname)

    out_fname = join(build_dir, f'dice_pools_d{n_sides}_c.png')
    dc_ocs = (
            (14, 22), (14, 27), (14, 30), 
            (15, 27), (15, 30), (15, 34), 
            (16, 27), (16, 30), (16, 34), 
            (17, 27), (17, 30), (17, 34), 
            (18, 29), (18, 32), (18, 36), 
            (19, 29), (19, 32), (19, 36), 
    )
    generate_dice_pool_graph(dc_ocs=dc_ocs, out_fname=out_fname)    

    
if __name__ == "__main__":
    #generate_dice_pool_graphs()

    difficulty = 13 + MAX_GROUNDING_DIFF
    n_dice = 3
    n_sides = 6
    # p = prob_sum_total_or_more(difficulty-1, n_dice, n_sides)
    p = prob_sum_total_or_more(difficulty+1, n_dice, n_sides)
    print(p)
