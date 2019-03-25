#!/usr/bin/python3
import pygal
from pygal import Config


hist = pygal.Histogram(
    human_readable=True,
    range=(0, 12),
    title="Dmg Bonus by Level for PCs.",
    x_title="PC Level",
    y_title="Dmg Bonus",
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
)


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


MAX_MAGIC_WEAPON_EXTRA_DMG = 3
AVG_D10_DMG = 5.5
AVG_D6_DMG = 3.5

max_bars = []
min_bars = []
max_bars_with_d10_magic_weapon = []
max_bars_with_d10_weapon = []
min_bars_with_d6_weapon = []
for i in range(1, 16):
    max_bars.append((max_level_bonus(i), i-0.5, i+0.5))
    min_bars.append((min_level_bonus(i), i-0.5, i+0.5))

    max_bars_with_d10_magic_weapon.append(
        (max_level_bonus(i) + AVG_D10_DMG + MAX_MAGIC_WEAPON_EXTRA_DMG, i-0.5, i+0.5))
    max_bars_with_d10_weapon.append((
        max_level_bonus(i) + AVG_D10_DMG, i-0.5, i+0.5))
    min_bars_with_d6_weapon.append(
        (min_level_bonus(i) + AVG_D6_DMG, i-0.5, i+0.5))

hist.add('Max',  max_bars)
hist.add('Min',  min_bars)
hist.render_to_png('pc_dmg_bonus_by_level.png')


#
#  Avg Damage.
#

hist2 = pygal.Histogram(
    human_readable=True,
    range=(0, 22),
    title="Average Dmg by Level for PCs.",
    x_title="PC Level",
    y_title="Average Dmg",
    legend_at_bottom=True,
    legend_at_bottom_columns=3,
    # fill=False,
)

hist2.add('d6 Weapon Dmg',
          min_bars_with_d6_weapon,
          # fill=False,
)
hist2.add('d10 Weapon Dmg',
          max_bars_with_d10_weapon,
          # fill=False,
)
hist2.add('d10 Weapon Dmg +3 Magic',
          max_bars_with_d10_magic_weapon,
          # fill=False,
          # color=(0, 1, 0),
)
hist2.render_to_png('pc_avg_dmg_by_level.png')
