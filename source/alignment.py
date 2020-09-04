import threading

from matplotlib import use
from matplotlib.pyplot import figure, close
import cv2
import numpy as np

from . import contours
from . import curves 

img = np.ones([500, 500, 3])
master_xs = []
master_ys = []
shift_factor_x = 0
shift_factor_y = 0
break_flag = False
skip_flag = False

def figure_to_array(fig:figure):
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    ret = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    ret.shape = (w, h, 4)
    return ret[:,:,1:4]

def align_data(xs, ys, indices, alignment_points):
    global master_xs, master_ys, break_flag, shift_factor_x, shift_factor_y, skip_flag
    use('Agg')
    
    for i in range(0, len(indices)): 
        if i + 1 < len(indices):
            slice_xs = xs[indices[i]:indices[i+1]]
            slice_ys = ys[indices[i]:indices[i+1]]
        else:
            slice_xs = xs[indices[i]:len(xs)]
            slice_ys = ys[indices[i]:len(ys)]

        slice_xs, slice_ys = curves.sort_data(slice_xs, slice_ys)
        slice_xs = np.add(slice_xs, -1*alignment_points[i][0])
        slice_xs = np.add(slice_xs, 12.23) # From measurement to alignment point

        if not skip_flag:
            # Creates a new thread with target function 
            t = threading.Thread(target = display, args=[slice_xs, slice_ys, alignment_points[i]])
            t.daemon = True
            t.start()
            t.join()

        if break_flag == True:
            skip_flag = True

        if i + 1 < len(indices):
            xs[indices[i]:indices[i+1]], ys[indices[i]:indices[i+1]], _, _ = gen_disp_pts(slice_xs, slice_ys, alignment_points[i][0], alignment_points[i][1])
        else:
            xs[indices[i]:len(xs)], ys[indices[i]:len(xs)], _, _ = gen_disp_pts(slice_xs, slice_ys, alignment_points[i][0], alignment_points[i][1])

        master_xs = xs[indices[0]:indices[1]]
        master_ys = ys[indices[0]:indices[1]]

    use('TkAgg')
    return xs, ys

def display(xs, ys, alignment_point):
    global img, break_flag, shift_factor_x, shift_factor_y

    shift_factor_x = 0
    shift_factor_y = 0
    
    disp_xs, disp_ys, cx, cy = gen_disp_pts(xs, ys, alignment_point[0], alignment_point[1])

    img = gen_fig_array(disp_xs, disp_ys, cx, cy)
    cv2.imshow("Image", img)

    while True:
        cv2.imshow("Image", img)
        t = cv2.waitKeyEx(0)
        if t == 32: # space
            cv2.destroyWindow("Image")
            break

        # Fine and coarse alignment controls
        elif t == 2490368: #up 
            shift_factor_y += .1
            refresh(xs, ys, alignment_point[0], alignment_point[1])
        elif t == 2621440: #down
            shift_factor_y -= .1
            refresh(xs, ys, alignment_point[0], alignment_point[1])
        elif t == 119: #w 
            shift_factor_y += 1
            refresh(xs, ys, alignment_point[0], alignment_point[1])
        elif t == 115: #s
            shift_factor_y -= 1
            refresh(xs, ys, alignment_point[0], alignment_point[1]) 

        elif t == 113: # (Q)uit
            cv2.destroyWindow("Image")
            break_flag = True
            break

def refresh(xs, ys, cx, cy):
    global img

    disp_xs, disp_ys, cx, cy = gen_disp_pts(xs, ys, cx, cy)

    img = gen_fig_array(disp_xs, disp_ys, cx, cy)
    cv2.imshow("Image", img)

def gen_fig_array(xs, ys, cx, cy):
    global master_xs, master_ys

    fig = figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    ax.scatter(master_xs, master_ys, color='black')
    ax.scatter(xs, ys, color='blue') 
    ax.scatter(cx, cy, color='green') 
    ax.plot([0, 0], [-5, 25], color='green')
    ax.plot([10.541, 10.541], [-5, 25])
    ax.plot([-9.779, -9.779], [-5, 25])
    ax.axis([-15, 15, -30, 0])

    fig.tight_layout()
    fig.set_size_inches(10, 10)

    ret = figure_to_array(fig)
    close(fig)
    return ret

def gen_disp_pts(xs, ys, cx, cy):
    global shift_factor_x, shift_factor_y
    disp_xs = np.add(xs, shift_factor_x)
    disp_ys = np.add(ys, shift_factor_y)
    cx += shift_factor_x
    cy += shift_factor_y

    disp_xs, disp_ys = contours.rotate_points(disp_xs, disp_ys, 0, cx, cy)

    return disp_xs, disp_ys, cx, cy