#!/usr/bin/python3
"""

  Graphs the number of 6s we'd expect to see when we roll n d6.

"""
import sys
from os.path import join
from math import comb, pow

from PIL import Image
import pygal
from pygal.style import DefaultStyle

from utils import build_dir


def prob_of_n6s(n_dice, min_prob=None):
    total = float(pow(6, n_dice))
    probs = []
    for number_of_d6s in range(0, n_dice+1):
        n_not_6 = n_dice - number_of_d6s
        count = comb(n_dice, n_not_6) * pow(5, n_not_6)
        prob = 100.0 * count/total
        #print(f"dice: {n_dice},  n_6: {number_of_d6s}|{n_not_6},  count:{count} prob:{prob}.")
        if min_prob is not None and prob < min_prob:
            break
        probs.append(prob)        
    return probs


def draw_d6_graph():    
    """
      Graph comparison 
    """
    hist = pygal.Line(
        human_readable=True,
        title="Probability of Getting n 6s",
        x_title="Number of 6s rolled",
        y_title="Probability",
        legend_at_bottom=False,
        legend_at_bottom_columns=5,
        x_label_rotation=15,
    )

    min_prob = 0.05 # percent
    hist.add('1d6', prob_of_n6s(1, min_prob))
    hist.add('2d6', prob_of_n6s(2, min_prob))
    hist.add('3d6', prob_of_n6s(3, min_prob))
    hist.add('4d6', prob_of_n6s(4, min_prob))
    hist.add('5d6', prob_of_n6s(5, min_prob))
    hist.add('6d6', prob_of_n6s(6, min_prob))
    hist.add('7d6', prob_of_n6s(7, min_prob))
    hist.add('8d6', prob_of_n6s(8, min_prob))
    hist.add('9d6', prob_of_n6s(9, min_prob))
    hist.add('10d6', prob_of_n6s(10, min_prob))
    hist.add('11d6', prob_of_n6s(11, min_prob))
    hist.add('12d6     ', prob_of_n6s(12, min_prob))
    hist.x_labels = map(str,
                        [0, 1, "2 Lvl1 OC!", "3 Lvl2 OC!", "4 Lvl3 OC!", 5, 6, 7])

    fname = join(build_dir, 'n_d6s.png')
    hist.render_to_png(fname)


