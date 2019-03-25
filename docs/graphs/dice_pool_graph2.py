#!/usr/bin/python3
import pygal
from pygal.style import DefaultStyle
from dice_pools import *


#difficulty = 10
#overcharge = difficulty + 4
n_sides = 6
dice_pool_range = range(1, 10)
#dice_pool_range_2_8 = range(2, 8)
#dice_pool_range_3_9 = range(3, 9)


def create_img(fname, difficulty, overcharge,
               # dice_pool_range,
               show_legend=False):
    line_chart = pygal.Line(
        print_values=True,
        show_legend=show_legend,
        #height=0,
        #width=1,
        legend_at_bottom=True,
        style=DefaultStyle(
            value_font_family='googlefont:Raleway',
            value_font_size=13,            
        ))
    line_chart.value_formatter = lambda x: "%.0f%%" % (100 * x) if x > 0.04 else ""
    line_chart.title = (
        f'Difficulty {difficulty} with Overcharge {overcharge}')

    line_chart.y_title = "Probability"
    line_chart.x_title = "Number of Dice Rolled."
    line_chart.x_labels = [str(x) for x in dice_pool_range]


    overcharge_with_grounding = overcharge + 3
    
    # for d in dice_pool_range:
    #     print("%s %s " %
    #           (prob_sum_total_or_less(difficulty-1, d, n_sides),
    #            prob_sum_total_or_less(overcharge-1, d, n_sides)))

    line_chart.add(
        "Undercharged",
        [
            prob_sum_total_or_less(difficulty-1, d, n_sides)
            for d in dice_pool_range
        ])

    line_chart.add(
        "OK",
        [
            (
                prob_sum_total_or_less(overcharge-1, d, n_sides) #-
                #prob_sum_total_or_less(difficulty-1, d, n_sides)
            )
            for d in dice_pool_range
        ])

    line_chart.add(
        "Grounding",
        [
            (
                prob_sum_total_or_less(overcharge_with_grounding-1, d, n_sides) #-
                #prob_sum_total_or_less(overcharge-1, d, n_sides)
            )
            for d in dice_pool_range
        ]
    )

    line_chart.add(
        "Overcharge",
        [
            1 - prob_sum_total_or_more(overcharge_with_grounding, d, n_sides)
            for d in dice_pool_range
        ])
    line_chart.render_to_png(fname)


    

fnames = []
first_img = True
for difficulty, overcharge in (
        (2, 7), (3, 7),  (4, 7), 
        (5, 11), (6, 11), (7, 11), 
        (8, 15), (9, 15), (10, 15),
        (11, 19), (12, 19), (13, 19), 
        (14, 23), (15, 23), (16, 23), 
        (17, 27), (18, 27), (19, 27), 
):
    fname = f'dice_pool_{difficulty}_{overcharge}.png'
    #create_img(fname, difficulty, overcharge, show_legend=first_img)
    #create_img(fname, difficulty, overcharge, show_legend=False)
    create_img(fname, difficulty, overcharge, show_legend=False)
    fnames.append(fname)
    first_img = False

import sys
from PIL import Image

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

print((width, height))

new_img = Image.new('RGB', (width, height))

x_offset = 0
y_offset = 0
row_number = 0
y = 0
for img_row in img_rows:
    x_offset = 0
    print("++++++++++++++++++++++++++++++++")
    print(img_row)
    print(img_row.__class__)
    print(img_rows[0].__class__)
    #print(img_row[0].__class__)
    print(f" y offset {y_offset}")
    for img in img_row:
        new_img.paste(img, (x_offset, y_offset))
        #pos = (x_offset, y * 100)
        #print(pos)
        #new_img.paste(img, pos)
        x_offset += img.size[0]
    y_offset += row_heights[row_number]    
    row_number += 1

new_img.save('dice_pools.png')
