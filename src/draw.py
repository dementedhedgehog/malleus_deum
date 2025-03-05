"""

  Draws graphs, splines etc using Cairo.



"""
import cairo

SPLINE_VERTICAL_LEAD = 18


# A spline is a list of points.

def add_spline_points(spline):
    """Sums all the offsets in a set of spline points."""
    x = 0
    y = 0
    for point in spline:
        xp, yp = point
        x += xp
        y += yp
    return x, y


def calc_spline_offsets(offset, spline):
    last_point = offset
    offset_spline_points = []
    for x, y in spline:
        new_point = (x + last_point[0], y + last_point[1])
        offset_spline_points.append(new_point)
        last_point = new_point
    return offset_spline_points


def draw_spline(context, spline, lead=SPLINE_VERTICAL_LEAD):
    """
    Points are absolute points along which we will draw our arrow.

    """
    n = len(spline)-1
    for i in range(0, n):
        p1 = spline[i]
        p2 = spline[i+1]
        
        # draw arrow
        x0, y0 = p1
        x3, y3 = p2
        x1, y1 = x0, y0 + lead
        x2, y2 = x3, y3 - lead
        
        context.move_to(x0, y0)
        context.curve_to(x1, y1, x2, y2, x3, y3)
        context.stroke()
        if i == n:
            draw_square(context, *p2)        
    return


def draw_square(context, x, y):
    # Draw square
    original_pos = context.get_current_point()
    RADIUS = 1
    context.rectangle(x - RADIUS, y - RADIUS, 2*RADIUS, 2*RADIUS)
    context.stroke()
    context.move_to(*original_pos)


# def draw_spline(context, points, lead=SPLINE_VERTICAL_LEAD):
#     """
#     Points are absolute points along which we will draw our arrow.

#     """
#     n = len(points)-1
#     for i in range(0, n):
#         p1 = points[i]
#         p2 = points[i+1]
        
#         # draw arrow
#         x0, y0 = p1
#         x3, y3 = p2
#         x1, y1 = x0, y0 + lead
#         x2, y2 = x3, y3 - lead
        
#         context.move_to(x0, y0)
#         context.curve_to(x1, y1, x2, y2, x3, y3)
#         context.stroke()
#         if i == n:
#             draw_square(context, *p2)
#     return
    
