#!/usr/bin/python3
from os.path import join
import pygal
from pygal import Config
from utils import build_dir


MAX_LEVEL = 20
MAX_MAGIC_WEAPON_EXTRA_DMG = 3
MAX_D12_DMG = 12
AVG_D12_DMG = 6.5
AVG_D10_DMG = 5.5
AVG_D8_DMG = 4.5
AVG_D6_DMG = 3.5
AVG_2D12 = 13
PROB_60PC = 12
LEVELS = range(1, MAX_LEVEL+1)
LEVELS_STR = list(map(str, LEVELS))

#
# 
#
MIN_PRIMARY_ABILITY_AT_LEVEL_1 = 9
MAX_PRIMARY_ABILITY_AT_LEVEL_1 = 17




AVG_NUMBER_OF_HITS_TO_KILL_GRUNT = 2.0

# (x, p) prob p for getting at least a value of x from anydice.com
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
probs_d20 = [100.0 - (level-1) * 5 for level in LEVELS] + [0.0, 0.0, 0.0, 0.0]

# anydice output [lowest 2 of 3d12] .. export at-least
probs_3d12_lowest_2 = (
    100.0,              # 1
    100.0,              # 2
    98.03240740741,      # 3
    94.38657407408,      # 4
    89.29398148149001,   # 5
    83.04398148149001,   # 6
    75.86805555556,      # 7
    68.05555555556,      # 8
    59.83796296297,      # 9
    51.50462962964001,   # 10
    43.287037037050005,  # 11
    35.474537037050005,  # 12  
    28.298611111120007,  # 13
    22.048611111120007,  # 14
    16.782407407420006,  # 15
    12.442129629640007,  # 16
    8.912037037050007,   # 17
    6.134259259270007,   # 18
    3.9930555555700074,  # 19
    2.4305555555700074,  # 20
    1.3310185185300074,  # 21
    0.6365740740860074,  # 22
    0.2314814814930074,  # 23
    0.0578703703820074,  # 24
)


# anydice output [highest 2 of 3d12] .. export at-least
probs_3d12_highest_2 = (
    100.0,              # 1
    100.0,              # 2
    99.9421296296296,   # 3
    99.7685185185186,   # 4
    99.36342592592561,  # 5
    98.66898148148161,  # 6
    97.56944444444161,  # 7
    96.00694444444161,  # 8
    93.86574074074161,  # 9
    91.08796296296161,  # 10
    87.55787037037162,  # 11
    83.21759259259161,  # 12
    77.95138888889161,  # 13
    71.70138888889161,  # 14
    64.52546296296161,  # 15
    56.71296296296161,  # 16
    48.49537037037161,  # 17
    40.162037037041614, # 18
    31.944444444451612, # 19
    24.131944444451612, # 20
    16.956018518521613, # 21
    10.706018518521613, # 22
    5.6134259259316135, # 23
    1.9675925926016133, # 24
)




#
#  Graph comparison d20 and 2d12
#
bars_2d12 = []
bars_d20 = []
for i in range(1, 25):
    bars_2d12.append(probs_2d12[i-1])
    bars_d20.append(probs_d20[i-1])

comparison_d20_vs_2d12_hist = pygal.Line(
    human_readable=True,
    title="Probability of Getting At Least n on a Std Check 2d12 vs d20",
    x_title="n",
    y_title="Probability",
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
)

comparison_d20_vs_2d12_hist.add('Std Check 2d12', bars_2d12)
comparison_d20_vs_2d12_hist.add('d20',  bars_d20)
comparison_d20_vs_2d12_hist.x_labels = map(str, range(1, 25))
fname = join(build_dir, 'std_check_2d12_vs_d20.png')
comparison_d20_vs_2d12_hist.render_to_png(fname)


#
#  Graph comparison 2d12, 3d12 pick lowest 2, 3d12 pick highest 2
#
def graph_advantage_disadvantage():
    bars_2d12 = []
    bars_3d12_lowest_2 = []
    bars_3d12_highest_2 = []
    for i in range(1, 25):
        bars_2d12.append(probs_2d12[i-1])
        bars_3d12_lowest_2.append(probs_3d12_lowest_2[i-1])
        bars_3d12_highest_2.append(probs_3d12_highest_2[i-1])

    hist = pygal.Line(
        human_readable=True,
        title="Probability of Getting At Least n on a Std Check 2d12 vs 3d12 Advantage or Disadvantage",
        x_title="n",
        y_title="Probability",
        legend_at_bottom=True,
        legend_at_bottom_columns=3,
    )

    hist.add('Std Check 2d12', bars_2d12)
    hist.add('3d12 Advantage', bars_3d12_highest_2)
    hist.add('3d12 Disadvantage', bars_3d12_lowest_2)
    hist.x_labels = map(str, range(1, 25))
    fname = join(build_dir, 'std_check_2d12_advantage_vs_disadvantage.png')
    hist.render_to_png(fname)
graph_advantage_disadvantage()



def smooth(dmgs):
    last_dmg = dmgs[0]
    next_dmg = 0
    for i in range(len(dmgs)):

        if i < len(dmgs) - 1:
            next_dmg = dmgs[i+1]
        else:
            next_dmg = dmgs[i]

        dmg = (0.5 * dmgs[i]) + (0.25 * last_dmg) + (0.25 * next_dmg)
        last_dmg = dmg

        dmgs[i] = dmg
    return dmgs


def get_min_dmg_lvl_multiplier(level):
    if level > 16:
        multiplier = 4
    elif level > 10:
        multiplier = 3
    elif level > 5:
        multiplier = 2
    else:
        multiplier = 1
    return multiplier

def get_max_dmg_lvl_multiplier(level):
    if level > 14:
        multiplier = 4
    elif level > 9:
        multiplier = 3
    elif level > 4:
        multiplier = 2
    else:
        multiplier = 1
    return multiplier

def get_avg_dmg_lvl_multiplier(level):
    return (get_min_dmg_lvl_multiplier(level) + get_max_dmg_lvl_multiplier(level)) / 2.0



#
# ability Range (provides modifiers).
#
def min_ability(level):
    ability = 11 + 2*(level-1)//8
    # if x >= 3:
    #     to_hit += 1
    # if x >= 6:
    #     to_hit += 1
    # if x >= 11:
    #     to_hit += 1
    # return to_hit
    return ability


def max_ability(level):
    # to_hit = min_to_hit_bonus(x) + 2
    # if x >= 2:
    #     to_hit += 1
    # if x >= 8:
    #     to_hit += 1
    # return to_hit
    return min_ability(level-1) + 5


def avg_ability(level):
    return (min_ability(level) + max_ability(level))/2

min_abilities = {}
avg_abilities = {}
max_abilities = {}
for level in LEVELS:
    min_abilities[level] = min_ability(level)
    max_abilities[level] = max_ability(level)
    avg_abilities[level] = avg_ability(level)

    
ability_hist = pygal.Line(
    human_readable=True,
    range=(0, max(max_abilities)),
    x_title="Level",
    y_title="Ability Range",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    interpolation_precision=3,
)
ability_hist.add('Min Ability Score',  min_abilities.values())
ability_hist.add('Average Ability Score',  avg_abilities.values())
ability_hist.add('Max Ability Score',  max_abilities.values())
ability_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'ability_range_by_level.png')
ability_hist.render_to_png(fname)



#
# Ability Bonuses
#
min_ability_bonuses = {}
avg_ability_bonuses = {}
max_ability_bonuses = {}
for level in LEVELS:    
    min_ability_bonuses[level] = min_abilities[level] - 13
    max_ability_bonuses[level] = max_abilities[level] - 13
    avg_ability_bonuses[level] = avg_abilities[level] - 13

    

ability_hist = pygal.Line(
    human_readable=True,
    range=(min(min_ability_bonuses.values()) - 1, max(max_ability_bonuses.values())),
    x_title="Level",
    y_title="Ability Bonus",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    interpolation_precision=3,
)
ability_hist.add('Min Ability Bonus',  min_ability_bonuses.values())
ability_hist.add('Average Ability Bonus',  avg_ability_bonuses.values())
ability_hist.add('Max Ability Bonus',  max_ability_bonuses.values())
ability_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'ability_bonus_by_level.png')
ability_hist.render_to_png(fname)



#
# Skill Level Bonus
#
def min_skill_bonus(level):
    skill = 0  # (x//3-1)
    if level >= 3:
        skill += 1
    if level >= 4:
        skill += 1
    if level >= 6:
        skill += 1
    if level >= 11:
        skill += 1
    #if level >= 15:
    #    skill += 1
    return skill


def max_skill_bonus(level):
    skill = min_skill_bonus(level) + 3
    #if level >= 10:
    #    skill += 1
    # if level >= 2:
    #     skill += 1
    # if level >= 8:
    #     skill += 1
    return skill

def avg_skill_bonus(level):
    return (min_skill_bonus(level) + max_skill_bonus(level))/2

min_skill = []
avg_skill = []
max_skill = []
for level in LEVELS:
    min_skill.append(min_skill_bonus(level))
    avg_skill.append(avg_skill_bonus(level))
    max_skill.append(max_skill_bonus(level))

skill_hist = pygal.Line(
    human_readable=True,
    range=(0, max(max_skill)),
    x_title="PC Level",
    y_title="Skill Level Bonus",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    interpolation_precision=3,
)
skill_hist.add('Min',  min_skill)
skill_hist.add('Avg',  avg_skill)
skill_hist.add('Max',  max_skill)
skill_hist.x_labels = map(str, LEVELS)
skill_fname = join(build_dir, 'skill_bonus_by_level.png')
skill_hist.render_to_png(skill_fname)




#
# To-Hit Table
# 
# This will represent the maximum level
# attainable at that level
#

def min_to_hit_bonus(level):
    return avg_skill[level-1] + avg_ability_bonuses[level]

def max_to_hit_bonus(level):
    return max_skill[level-1] + max_ability_bonuses[level]

def avg_to_hit_bonus(level):
    return (min_to_hit_bonus(level) + max_to_hit_bonus(level))/2


min_to_hit = []
avg_to_hit = []
max_to_hit = []
for level in LEVELS:
    min_to_hit.append(min_to_hit_bonus(level))
    avg_to_hit.append(avg_to_hit_bonus(level))
    max_to_hit.append(max_to_hit_bonus(level))

to_hit_hist = pygal.Line(
    human_readable=True,
    range=(0, max(max_to_hit)),
    x_title="PC Level",
    y_title="PC To Hit Bonus",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    interpolation_precision=3,
)
to_hit_hist.add('Min',  min_to_hit)
to_hit_hist.add('Avg',  avg_to_hit)
to_hit_hist.add('Max',  max_to_hit)
to_hit_hist.x_labels = map(str, LEVELS)
to_hit_fname = join(build_dir, 'to_hit_bonus_by_level.png')
to_hit_hist.render_to_png(to_hit_fname)



#
# Defensive DC by Level. 
#

# Keep the monster attacks in line with the PC attacks.
avg_low_dc = []
avg_medium_dc = []
avg_high_dc = []
max_low_dc = []
max_medium_dc = []
max_high_dc = []
for level in LEVELS:
    avg_to_hit = PROB_60PC + avg_to_hit_bonus(level)
    avg_low_dc.append(avg_to_hit-3)
    avg_medium_dc.append(avg_to_hit)
    avg_high_dc.append(avg_to_hit+3)
    
    max_to_hit = PROB_60PC + max_to_hit_bonus(level)
    max_low_dc.append(max_to_hit-3)
    max_medium_dc.append(max_to_hit)
    max_high_dc.append(max_to_hit+3)


rbg_style = pygal.style.Style(
    colors=['#FF0000', '#0000FF', '#00FF00'],
)
max_style = {
    'width': 2,
    'dasharray': '3, 6',
    'linecap': 'round',
    'linejoin': 'round',
    'color': 'red'
}
defensive_dc_hist = pygal.Line(
    human_readable=True,
    range=(0, max(max_high_dc)+1),
    x_title="PC Level",
    y_title="Defence DC",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    x_labels = map(str, LEVELS),
    style=rbg_style
)

defensive_dc_hist.add('Avg 38% To-Hit Probability',  avg_high_dc)
defensive_dc_hist.add('Avg 62% To-Hit Probability',  avg_medium_dc)
defensive_dc_hist.add('Avg 81% To-Hit Probability',  avg_low_dc)
defensive_dc_hist.add('Max 38% To-Hit Probability',  max_high_dc, stroke_style=max_style)
defensive_dc_hist.add('Max 62% To-Hit Probability',  max_medium_dc, stroke_style=max_style)
defensive_dc_hist.add('Max 81% To-Hit Probability',  max_low_dc, stroke_style=max_style)
defensive_dc_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'defence_difficulty_by_level.png')
defensive_dc_hist.render_to_png(fname)


#
# Monster To Hit Bonus By Level.
#

# Keep the monster attacks in line with the PC attacks.
avg_low_dc = []
avg_medium_dc = []
avg_high_dc = []
max_low_dc = []
max_medium_dc = []
max_high_dc = []
for level in LEVELS:
    avg_to_hit = PROB_60PC # + avg_to_hit_bonus(level)
    avg_low_dc.append(avg_to_hit + min_skill_bonus(level))
    avg_medium_dc.append(avg_to_hit + avg_skill_bonus(level)) 
    avg_high_dc.append(avg_to_hit + max_skill_bonus(level))


rbg_style = pygal.style.Style(
    colors=['#FF0000', '#0000FF', '#00FF00'],
)
max_style = {
    'width': 2,
    'dasharray': '3, 6',
    'linecap': 'round',
    'linejoin': 'round',
    'color': 'red'
}
monster_attack_dc_hist = pygal.Line(
    human_readable=True,
    range=(0, max(avg_high_dc)+1),
    x_title="Monster Level",
    y_title="Monster Attack DC",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    x_labels = map(str, LEVELS),
    style=rbg_style
)

monster_attack_dc_hist.add('Avg 54% To-Hit Probability',  avg_high_dc)
monster_attack_dc_hist.add('Avg 31% To-Hit Probability',  avg_medium_dc)
monster_attack_dc_hist.add('Avg 15% To-Hit Probability',  avg_low_dc)
monster_attack_dc_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'monster_attack_bonus_by_level.png')
monster_attack_dc_hist.render_to_png(fname)






# #
# # Raw Defence DC by Level. 
# #

# #
# avg_low_dc = []
# avg_medium_dc = []
# avg_high_dc = []
# max_low_dc = []
# max_medium_dc = []
# max_high_dc = []
# for level in LEVELS:
#     avg_to_hit = PROB_60PC + avg_to_hit_bonus(level)
#     avg_low_dc.append(avg_to_hit-3)
#     avg_medium_dc.append(avg_to_hit)
#     avg_high_dc.append(avg_to_hit+3)
    
#     max_to_hit = PROB_60PC + max_to_hit_bonus(level)
#     max_low_dc.append(max_to_hit-3)
#     max_medium_dc.append(max_to_hit)
#     max_high_dc.append(max_to_hit+3)


# rbg_style = pygal.style.Style(
#     colors=['#FF0000', '#0000FF', '#00FF00'],
# )
# max_style = {
#     'width': 2,
#     'dasharray': '3, 6',
#     'linecap': 'round',
#     'linejoin': 'round',
#     'color': 'red'
# }
# hist3 = pygal.Line(
#     human_readable=True,
#     range=(0, max(max_high_dc)+1),
#     x_title="Level",
#     y_title="Defence DC and Monster Attack DC",
#     show_x_guides=True,
#     show_y_guides=True,
#     legend_at_bottom=True,
#     legend_at_bottom_columns=3,
#     x_labels = map(str, LEVELS),
#     style=rbg_style
# )


# hist3.add('Avg 38% To Hit Probability',  avg_high_dc)
# hist3.add('Avg 62% To-Hit Probability',  avg_medium_dc)
# hist3.add('Avg 81% To-Hit Probability',  avg_low_dc)
# hist3.add('Max 38% To Hit Probability',  max_high_dc, stroke_style=max_style)
# hist3.add('Max 62% To-Hit Probability',  max_medium_dc, stroke_style=max_style)
# hist3.add('Max 81% To-Hit Probability',  max_low_dc, stroke_style=max_style)
# hist3.x_labels = map(str, LEVELS)
# fname = join(build_dir, 'defensive_check_difficulty_by_level.png')
# hist3.render_to_png(fname)




# #
# # PC Armour by Level.
# #
# # hist2 = pygal.Line(
# #     human_readable=True,
# #     x_title="PC Level",
# #     y_title="Defence DC",
# #     show_x_guides=True,
# #     legend_at_bottom=True,
# #     legend_at_bottom_columns=3,
# # )


# # # Keep the monster attacks in line with the PC attacks.
# # min_ac = []
# # avg_ac = []
# # max_ac = []
# # for i in LEVELS:
# #     min_ac.append(9 + min_to_hit_bonus(i))
# #     avg_ac.append(13 + max_to_hit_bonus(i))
# #     max_ac.append(16 + max_to_hit_bonus(i))

# # hist2.add('Min',  min_ac)
# # hist2.add('Avg',  avg_ac)
# # hist2.add('Max',  max_ac)
# # hist2.x_labels = map(str, LEVELS)
# # fname = join(build_dir, 'pc_defence_dc_by_level.png')
# # hist2.render_to_png(fname)
















#
# Damage Calculations
#


max_lvl_multiplier = []
min_lvl_multiplier = []
avg_lvl_multiplier = []

for i in LEVELS:
    max_lvl_multiplier.append(get_max_dmg_lvl_multiplier(i))
    min_lvl_multiplier.append(get_min_dmg_lvl_multiplier(i))
    avg_lvl_multiplier.append(get_avg_dmg_lvl_multiplier(i))

dmg_level_multiplier_hist = pygal.Line(
    human_readable=True,
    range=(0, 5),
    x_title="PC Level",
    y_title="Damage Multiplier",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    x_labels = LEVELS_STR)

dmg_level_multiplier_hist.add('Max Dmg Multiplier',  max_lvl_multiplier)
dmg_level_multiplier_hist.add('Avg Dmg Multiplier',  avg_lvl_multiplier)
dmg_level_multiplier_hist.add('Min Dmg Multiplier',  min_lvl_multiplier)

fname = join(build_dir, 'pc_dmg_multiplier_by_level.png')
dmg_level_multiplier_hist.render_to_png(fname)




#
#  Avg PC Damage.
#
# weapon damage * weapon multiplier?
# + magic
# + primary ability
# 
max_dmg = []
min_dmg = []
max_with_d12_magic_weapon = []
max_with_d12_weapon = []
avg_with_d12_weapon = []
avg_with_d10_weapon = []
avg_with_d8_weapon = []
avg_with_d6_weapon = []
min_with_d6_weapon = []


for i in LEVELS:
    lvl_multiplier = get_avg_dmg_lvl_multiplier(i)
    
    max_with_d12_magic_weapon.append(        
        max_ability_bonuses[i] +
        (MAX_D12_DMG * lvl_multiplier) +
        MAX_MAGIC_WEAPON_EXTRA_DMG)

    max_with_d12_weapon.append(
        max_ability_bonuses[i] +
        (MAX_D12_DMG * lvl_multiplier))

    avg_with_d12_weapon.append(
        avg_ability_bonuses[i] +
        (AVG_D12_DMG * lvl_multiplier))

    avg_with_d10_weapon.append(
        avg_ability_bonuses[i] +
        (AVG_D10_DMG * lvl_multiplier))

    avg_with_d8_weapon.append(
        avg_ability_bonuses[i] +
        (AVG_D8_DMG * lvl_multiplier))

    avg_with_d6_weapon.append(
        avg_ability_bonuses[i] +
        (AVG_D6_DMG * lvl_multiplier))

    min_with_d6_weapon.append(
        (min_ability_bonuses[i] +
         AVG_D6_DMG * lvl_multiplier))

pc_avg_dmg_hist = pygal.Line(
    human_readable=True,
    range=(0, 60),
    x_title="PC Level",
    y_title=("Average Weapon Dmg\n"
             "(wpn dmg + ability bonus + magic bonus??)"),
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    x_labels = LEVELS_STR,
)

pc_avg_dmg_hist.add('Min d6 Wpn Dmg', min_with_d6_weapon)
pc_avg_dmg_hist.add('Avg d6 Wpn Dmg', avg_with_d6_weapon)
pc_avg_dmg_hist.add('Avg d10 Wpn Dmg', avg_with_d10_weapon)
pc_avg_dmg_hist.add('Avg d8 Wpn Dmg', avg_with_d8_weapon)
pc_avg_dmg_hist.add('Avg d12 Wpn Dmg', avg_with_d12_weapon)
pc_avg_dmg_hist.add('Max d12 Wpn Dmg +3 Magic', max_with_d12_magic_weapon)
fname = join(build_dir, 'pc_avg_dmg_by_level.png')
pc_avg_dmg_hist.render_to_png(fname)



#
#  Avg Monster HP.
#
monster_hp_hist = pygal.Line(
    range=(0, 65),
    human_readable=True,
    x_title="Monster Level",
    y_title="Average HP",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=5)

monster_hp_hist.add(
    'Minion',
    smooth([0.5 * AVG_NUMBER_OF_HITS_TO_KILL_GRUNT*d for d in avg_with_d6_weapon]))
monster_hp_hist.add(
    'Low',
    smooth([AVG_NUMBER_OF_HITS_TO_KILL_GRUNT*d for d in avg_with_d6_weapon]))
monster_hp_hist.add(
    'Medium-Low',
    smooth([AVG_NUMBER_OF_HITS_TO_KILL_GRUNT*d for d in avg_with_d8_weapon]))
monster_hp_hist.add(
    'Medium-High',
    smooth([AVG_NUMBER_OF_HITS_TO_KILL_GRUNT*d for d in avg_with_d10_weapon]))
monster_hp_hist.add(
    'High',
    smooth([AVG_NUMBER_OF_HITS_TO_KILL_GRUNT*d for d in avg_with_d12_weapon]))
monster_hp_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'monster_hp_by_level.png')
monster_hp_hist.render_to_png(fname)



#
#  Avg PC HP.
#

low = smooth([3*d for d in avg_with_d10_weapon])
avg = smooth([4*d for d in avg_with_d10_weapon])
high = smooth([5*d for d in avg_with_d10_weapon])
max_hp = max(high)

pc_hp_hist = pygal.Line(
    human_readable=True,
    x_title="Player Character Level",
    y_title="Average Player Character HP",
    show_x_guides=True,
    range=(0, max_hp), 
    legend_at_bottom=True,
    legend_at_bottom_columns=3)

pc_hp_hist.add('Low', low)
pc_hp_hist.add('Avg', avg)
pc_hp_hist.add('High', high)
pc_hp_hist.x_labels = map(str, LEVELS)
fname = join(build_dir, 'pc_hp_by_level.png')
pc_hp_hist.render_to_png(fname)




