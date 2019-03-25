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

probs_d20 = [100.0 - (x-1) * 5 for x in range(1, 21)] + [0.0, 0.0, 0.0, 0.0]


bars_2d12 = []
bars_d20 = []
for i in range(1, 25):
    bars_2d12.append(probs_2d12[i-1])
    bars_d20.append(probs_d20[i-1])

# hist = pygal.Histogram(
hist = pygal.Line(
    human_readable=True,
    title="Probability of Getting At Least n on a Std Check 2d12 vs d20",
    x_title="n",
    y_title="Probability",
    legend_at_bottom=True,
    legend_at_bottom_columns=2,
)

hist.add('Std Check 2d12', bars_2d12)
hist.add('d20',  bars_d20)
hist.x_labels = map(str, range(1, 25))
hist.render_to_png('std_check_2d12_vs_d20.png')
