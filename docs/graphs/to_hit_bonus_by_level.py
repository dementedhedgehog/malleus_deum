#!/usr/bin/python3
import pygal
from pygal import Config

# (x, p) prob p for getting at least a value of x
# from anydice.com
probs_2d12 = (
    100.0, # 1
    100.0, # 2
    99.3,  # 3
    97.9,  # 4
    95.8,  # 5
    93.0,  # 6
    89.6,  # 7
    85.4,  # 8
    80.5,  # 9
    75.0,  # 10
    68.7,  # 11
    61.8,  # 12
    54.2,  # 13
    45.8,  # 14
    38.2,  # 15
    31.3,  # 16
    25.0,  # 17
    19.4,  # 18
    14.6,  # 19
    10.4,  # 20
    6.9,   # 21
    4.2,   # 22
    2.1,   # 23
    0.7,   # 24    
)



#
# Player Character To-Hit Table
#
hist = pygal.Line(
    human_readable=True,
    range=(0, 15),
    x_labels = map(str, range(1, 15)),
    x_title="PC Level",
    y_title="To Hit Bonus",
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
)

def min_to_hit_bonus(x):
    to_hit = 2*(x-1)//5
    if x >= 2:
        to_hit += 1
    if x >= 5:
        to_hit += 1
    if x >= 10:
        to_hit += 1
    return to_hit


def max_to_hit_bonus(x):
    to_hit = min_to_hit_bonus(x)  
    if x >= 2:
        to_hit += 1
    if x >= 8:
        to_hit += 1
    return to_hit

min_to_hit = []
max_to_hit = []
for i in range(1, 20):
    min_to_hit.append(min_to_hit_bonus(i))
    max_to_hit.append(max_to_hit_bonus(i))

hist.add('Min',  min_to_hit)
hist.add('Max',  max_to_hit)
hist.render_to_png('to_hit_bonus_by_level.png')




#
# Monster Attack Difficulty by Level.
#
hist2 = pygal.Line(
    human_readable=True,
    #title="Attack Difficulty for Monsters by Level.",
    x_title="Monster Level",
    y_title="Attack Difficulty",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
)

AVG_2D12 = 13

# Keep the monster attacks in line with the PC attacks.
min_ac = []
avg_ac = []
max_ac = []
for i in range(1, 16):
    min_ac.append(9 + min_to_hit_bonus(i))
    avg_ac.append(13 + max_to_hit_bonus(i))
    max_ac.append(16 + max_to_hit_bonus(i))

hist2.add('Min',  min_ac)
hist2.add('Avg',  avg_ac)
hist2.add('Max',  max_ac)
hist2.x_labels = map(str, range(1, 16))
hist2.render_to_png('monster_attack_difficulty_by_level.png')





#
# Monster Attack Difficulty by Level.
#
hist3 = pygal.Line(
    human_readable=True,
    #title="Monster AC by Level.",
    x_title="Monster Level",
    y_title="AC",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
)

AVG_2D12 = 13

# Keep the monster attacks in line with the PC attacks.
min_ac = []
avg_ac = []
max_ac = []
for i in range(1, 16):
    min_ac.append(9 + min_to_hit_bonus(i))
    avg_ac.append(13 + max_to_hit_bonus(i))
    max_ac.append(16 + max_to_hit_bonus(i))

hist3.add('Min',  min_ac)
hist3.add('Avg',  avg_ac)
hist3.add('Max',  max_ac)
hist3.x_labels = map(str, range(1, 16))
hist3.render_to_png('monster_ac_by_level.png')




#
# Player Character To-Hit Table
#
hist4 = pygal.Line(
    human_readable=True,
    range=(0, 15),
    x_labels = map(str, range(1, 15)),
    #title="To Hit Bonus by Level for PCs.",
    x_title="PC Level",
    y_title="To Hit Bonus",
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
)

min_to_hit = []
max_to_hit = []
for i in range(1, 20):
    min_to_hit.append(min_to_hit_bonus(i))
    max_to_hit.append(max_to_hit_bonus(i))

hist4.add('Min',  min_to_hit)
hist4.add('Max',  max_to_hit)
hist4.render_to_png('to_hit_bonus_by_level.png')
