
from collections import defaultdict
from itertools import product
from functools import lru_cache as cache
from os.path import join

import pygal
from PIL import Image

from utils import build_dir

FAIL = -1




@cache
def get_morale_rolls(n_dice):
    """
    Returns an interable containing all permutations of n d6
    """
    choices = (1, 2, 3, 4, 5, 6)
    n_choices = (choices, )*n_dice
    return list(product(*n_choices))


@cache
def fails(roll, dc):
    """
    Returns True if the sum of the dice is strictly less than the target dc.
    """
    return sum(roll) < dc


@cache
def get_unexhausted_dice_count(roll):
    """
    Returns the number of unexhausted dice in the dice roll.
    """
    return sum([d>=3 for d in roll])


def convert_to_probs(count_dict):
    total = float(sum(count_dict.values()))
    probs = defaultdict(float)
    for k, v in count_dict.items():
        probs[k] = v / total
    return probs


def add_probs(probs_dict1, probs_dict2, probs_dict2_weight, keys):
    """
    Sets dict1 = weight * probs_dict2 in place

    """
    for k in keys:
        probs_dict1[k] += probs_dict2[k] * probs_dict2_weight        
    return
        
        
def probs_to_str(probs):
    str_rep = ""
    for k in sorted(probs.keys()):
        v = probs[k]
        str_rep += f"{k:2}, {v:.3f}\n"
    return str_rep



def get_results(n_dice, dc):
    morale_rolls = get_morale_rolls(n_dice)
    morale_results = defaultdict(int)
    totals = defaultdict(int)

    for roll in list(morale_rolls):
        fails_check = fails(roll, dc=dc)
        n_unexhausted_dice = get_unexhausted_dice_count(roll)

        # results
        morale_results[(fails_check, n_unexhausted_dice)] += 1

        # totals
        if fails_check:
            # fail
            totals[FAIL] += 1
        else:
            # succeeded with some number of dice remaining in the pool
            totals[n_unexhausted_dice] += 1

    return totals



def calculate_morale_iterations(n_dice, dc, n_iterations):
    # a dict mapping from iteration in [1..n_dice] to dict[result->prob]    
    probs = {}
    if n_iterations < 1:
        return probs

    # run the first iteration
    totals = get_results(n_dice=n_dice, dc=dc)
    probs[1] = convert_to_probs(totals)

    keys = list(range(n_dice+1)) + [FAIL, ]

    # run subsequent iterations
    for i in range(2, n_iterations+1):
        consolidated_probs = defaultdict(float)
        last_probs = probs[i-1]
        for k in keys:
            # k is the number of dice remaining.
            new_totals = get_results(n_dice=k, dc=dc)
            new_probs = convert_to_probs(new_totals)            
            weight = last_probs[k]
            add_probs(consolidated_probs, new_probs, weight, keys)

        probs[i] = consolidated_probs
    return probs


def get_fail_probs_from_morale_iterations(probs):
    fail_probs = []
    for i in probs.keys():
        fail_probs.append(probs[i][FAIL])
    return fail_probs



def draw_morale_graph(fname, n_dice):
    n_iterations = 7
    line_chart = pygal.Line()
    line_chart.title = f'Morale with Dice Pool Size: {n_dice}'
    line_chart.y_title = 'Probability of Failure'
    line_chart.x_title = 'Number of Morale Checks Made'
    line_chart.x_labels = map(str, range(1, n_iterations+1))

    for dc in (3, 4, 5, 7, 9, 11):
        probs = calculate_morale_iterations(n_dice=n_dice, dc=dc, n_iterations=n_iterations)
        fail_probs = get_fail_probs_from_morale_iterations(probs)
        line_chart.add(f'DC:{dc}',fail_probs)

    line_chart.render_to_png(fname)

# for n_dice in (2, 3, 4, 5, 6, 7):
#     draw_morale_graph(n_dice)


def generate_morale_comparisons_graph(from_dice_pool_size, to_dice_pool_size, out_fname):
    """
    A dice pool graph is a composite of other graphs.

    """
    fnames = []

    # write out a bunch of little graphs, one per dc.
    for n_dice in range(from_dice_pool_size, to_dice_pool_size+1):
        fname = join(build_dir, f'morale_dice_pool_{n_dice}.png')
        #fname = f"morale_dice_pool_{n_dice}.png"    
        #graph_dc(fname, dc)
        draw_morale_graph(fname, n_dice)
        fnames.append(fname)

    # now load those images 
    imgs = []
    for img_fname in fnames:
        img = Image.open(img_fname)
        imgs.append(img)

    # create a legend image the same size as the other graphs
    # first_img = imgs[0]
    # width, height = first_img.size
    # legend_fname = join(build_dir, 'oc_pool_legend.png')
    # generate_legend(legend_fname, width, height)
    # img = Image.open(legend_fname)
    # imgs.append(img)
        
    # arrange the per-dc-graph imgs into rows of 2
    step = 2
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


    

#for n_dice in (2, 3, 4, 5, 6, 7):
#    draw_morale_graph(n_dice)
generate_morale_comparisons_graph(2, 7, "morale_dc_comparison.png")
