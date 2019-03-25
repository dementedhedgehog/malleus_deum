#!/usr/bin/python3
import pygal
from pygal import Config

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



hist = pygal.Line(
    human_readable=True,
    range=(0, 16),
    x_title="PC Level",
    y_title="Damage Bonus",
    show_x_guides=True,
    show_y_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
    x_labels = map(str, range(1, 16))
)


def get_dmg_lvl_multiplier(level):
    if level > 12:
        multiplier = 4
    elif level > 8:
        multiplier = 3
    elif level > 4:
        multiplier = 2
    else:
        multiplier = 1
    print((level, multiplier))
    return multiplier


def min_level_bonus(level):
    bonus = level//3
    if level >= 2:
        bonus += 1
    if level >= 7:
        bonus += 1
    return bonus


def max_level_bonus(level):
    bonus = min_level_bonus(level)
    if level >= 3:
        bonus += 1
    if level >= 8:
        bonus += 1
    return bonus


def avg_level_bonus(level):
    return (min_level_bonus(level) + max_level_bonus(level)) / 2


MAX_MAGIC_WEAPON_EXTRA_DMG = 3
AVG_D10_DMG = 5.5
AVG_D8_DMG = 4.5
AVG_D6_DMG = 3.5

max_bars = []
min_bars = []
max_bars_with_d10_magic_weapon = []
max_bars_with_d10_weapon = []
min_bars_with_d6_weapon = []


max_dmg = []
min_dmg = []
max_with_d10_magic_weapon = []
max_with_d10_weapon = []
avg_with_d8_weapon = []
min_with_d6_weapon = []

for i in range(1, 16):
    max_bars.append(max_level_bonus(i))
    min_bars.append(min_level_bonus(i))
    
    max_dmg.append(max_level_bonus(i))
    min_dmg.append(min_level_bonus(i))

    lvl_multiplier = get_dmg_lvl_multiplier(i)

    max_with_d10_magic_weapon.append(
        (max_level_bonus(i) +
         (AVG_D10_DMG * lvl_multiplier) +
         MAX_MAGIC_WEAPON_EXTRA_DMG))

    max_with_d10_weapon.append((
        max_level_bonus(i) +
        (AVG_D10_DMG * lvl_multiplier)))

    avg_with_d8_weapon.append((
        avg_level_bonus(i) +
        (AVG_D8_DMG * lvl_multiplier)))

    min_with_d6_weapon.append(
        (min_level_bonus(i) +
         AVG_D6_DMG * lvl_multiplier))
    
hist.add('Max',  max_bars)
hist.add('Min',  min_bars)
hist.render_to_png('pc_dmg_bonus_by_level.png')


#
#  Avg PC Damage.
#

hist2 = pygal.Line(
    human_readable=True,
    x_title="PC Level",
    y_title="Average Dmg",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=4)

hist2.add('d6 Weapon Dmg', min_with_d6_weapon)
hist2.add('d10 Weapon Dmg', max_with_d10_weapon)
hist2.add('d8 Weapon Dmg', avg_with_d8_weapon)
hist2.add('d10 Weapon Dmg +3 Magic', max_with_d10_magic_weapon)
hist2.x_labels = map(str, range(1, 16))
hist2.render_to_png('pc_avg_dmg_by_level.png')


#
#  Avg PC HP.
#

hist3 = pygal.Line(
    human_readable=True,
    x_title="PC Level",
    y_title="Average HP",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3)


hist3.add('Low', smooth([4*d for d in avg_with_d8_weapon]))
hist3.add('Avg', smooth([5*d for d in avg_with_d8_weapon]))
hist3.add('High', smooth([6*d for d in avg_with_d8_weapon]))
hist3.x_labels = map(str, range(1, 16))
hist3.render_to_png('pc_hp_by_level.png')


#
#  Avg Monster HP.
#
hist4 = pygal.Line(
    human_readable=True,
    x_title="Monster Level",
    y_title="Average HP",
    show_x_guides=True,
    legend_at_bottom=True,
    legend_at_bottom_columns=3)

hist4.add('Low', smooth([1.5*d for d in avg_with_d8_weapon]))
hist4.add('Avg', smooth([2*d for d in avg_with_d8_weapon]))
hist4.add('High', smooth([3*d for d in avg_with_d8_weapon]))
hist4.x_labels = map(str, range(1, 16))
hist4.render_to_png('monster_hp_by_level.png')
