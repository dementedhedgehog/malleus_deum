#!/usr/bin/python3
"""
  
  Aspect lifetime.  Use a simulation .. it's simplest.


DC		15 to succeed and go up a level
DC		24 to become complacent


"""
import collections
import random
from os.path import join
import pygal

from utils import build_dir

LEVEL_1 = 1
LEVEL_2 = 2
LEVEL_3 = 3

# get these numbers from the spreadsheet.
states = (LEVEL_1, LEVEL_2, LEVEL_3)
level_down = {LEVEL_1: 1.00,
              LEVEL_2: 0.96,
              LEVEL_3: 0.93}
level_up = {LEVEL_1: level_down[LEVEL_1] - 0.44,
            LEVEL_2: level_down[LEVEL_2] - 0.50,
            LEVEL_3: level_down[LEVEL_3] - 0.55}


# def aspect(level=1, count=0):
#     count += 1
#     r = random()
#     if r > level_down[level]:
#         level = max(1, level-1)

#     elif r > level_up[level]:        
#         level += 1

#     if level > 3:
#         return count

#     return aspect(level=level, count=count)



def simulate_aspect_lifetime(level=1, count=1):
    r1 = random.randrange(1, 12)
    r2 = random.randrange(1, 12)


    succeeded = False
    righteous = False
    # boon = False
    # bane = False
    

    mods = []
    
    # righteous outcome
    if (r1 + r2) >= 15:
        succeeded = True
        mods.append("succeeded")

    if (r1 + r2) >= 19:
        righteous = True
        mods.append("righteous")

    # boon or bane
    # if r1 == r2:
    #     if r1 in (2, 4, 6, 8, 10, 12):
    #         # boon
    #         boon = True
    #         mods.append("boon")
    #     elif r1 in (1, 3, 5, 7, 9, 11):
    #         # bane
    #         bane = True
    #         mods.append("bane")

    if succeeded:
        level += 1

    if righteous:
        level += 1

    # if boon: 
    #     level += 1
            
    if level > 3:
        return count

    # increment the aspect lifetime count
    count += 1    

    #if count == 2:
    #    return
    return simulate_aspect_lifetime(level=level, count=count)





def draw_aspect_lifetime_graph():
    # collect the data about aspect lifetime
    # (this is the number of checks before an aspect reaches level 4 and should be retired)
    counts = collections.defaultdict(int)
    n_trials = 10000
    for i in range(n_trials):
        count = simulate_aspect_lifetime()
        counts[count] += 1

    count_values = list(counts.keys())
    count_values.sort()
    max_count = max(counts.keys())

    print([str(x) for x in range(0, max_count+1)])
    
    # a list of probabilities to graph.
    count_probs = [counts[count]/float(n_trials) for count in range(0, max(counts.keys())+1)]
    
    hist = pygal.Line(
        human_readable=True,
        title="Distribution of Aspect Lifetimes by Number of Checks",
        x_title="Number of Aspect Checks Made Before an Aspect Reaches Level 4",
        y_title="Probability",
        x_labels = [str(x) for x in range(0, max_count+1)],
        x_label_rotation=20,
        show_legend=False,
    )
    hist.add('', count_probs)

    fname = join(build_dir, 'aspect_lifetime_graph.png')
    hist.render_to_png(fname)


draw_aspect_lifetime_graph()
    
#simulate_aspect_lifetime()
