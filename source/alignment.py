import threading

import matplotlib
import matplotlib.pyplot as plt
# matplotlib.use('Agg')
import cv2
import numpy as np

img = np.ones([500, 500, 3])
master_xs = []
master_ys = []
shift_factor_x = 0
shift_factor_y = 0
break_flag = False

def figure_to_array(fig:plt.figure):
    fig.canvas.draw()
    w,h = fig.canvas.get_width_height()
    ret = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8)
    ret.shape = (w, h, 4)

    return ret[:,:,1:4]

def align_data(xs, ys, indices):
    matplotlib.use('Agg')
    global master_xs, master_ys, break_flag, shift_factor_x, shift_factor_y

    master_xs = xs[indices[0]:indices[1]]
    master_ys = ys[indices[0]:indices[1]]

    for i in range(1, len(indices)): 
        if i + 1 < len(indices):
            slice_xs = xs[indices[i]:indices[i+1]]
            slice_ys = ys[indices[i]:indices[i+1]]
        else:
            slice_xs = xs[indices[i]:len(xs)]
            slice_ys = ys[indices[i]:len(ys)]

        data = np.concatenate((slice_xs, slice_ys), axis=0)
        temp = np.reshape(data, (-1, 2), 'F')
        np.sort(temp)

        slice_xs = temp[:,0]
        slice_ys = temp[:,1]

        # Creates a new thread with target function 
        t = threading.Thread(target = display, args=[slice_xs, slice_ys])
        t.daemon = True
        t.start()
        t.join()

        if break_flag == True:
            break
        else:
            if i + 1 < len(indices):
                xs[indices[i]:indices[i+1]] = np.add(xs[indices[i]:indices[i+1]], shift_factor_x)
                ys[indices[i]:indices[i+1]] = np.add(ys[indices[i]:indices[i+1]], shift_factor_y)
            else:
                xs[indices[i]:len(xs)] = np.add(xs[indices[i]:len(xs)], shift_factor_x)
                ys[indices[i]:len(xs)] = np.add(ys[indices[i]:len(ys)], shift_factor_y)

    matplotlib.use('TkAgg')
    return xs, ys

def display(xs, ys):
    global img, break_flag, shift_factor_x, shift_factor_y

    shift_factor_x = 0
    shift_factor_y = 0

    disp_xs = np.add(xs, shift_factor_x)
    disp_ys = np.add(ys, shift_factor_y)

    img = gen_fig_array(disp_xs, disp_ys)
    cv2.imshow("Image", img)

    while True:
        cv2.imshow("Image", img)
        t = cv2.waitKeyEx(0)
        if t == 110: # n
            cv2.destroyWindow("Image")
            break

        #Fine control 
        elif t == 2424832: #left
            shift_factor_x -= .1
            refresh(xs, ys)
        elif t == 2490368: #up 
            shift_factor_y += .1
            refresh(xs, ys)
        elif t == 2555904: #right
            shift_factor_x += .1
            refresh(xs, ys)
        elif t == 2621440: #down
            shift_factor_y -= .1
            refresh(xs, ys)

        #Coarse control
        elif t == 97: #left
            shift_factor_x -= 1
            refresh(xs, ys)
        elif t == 119: #up 
            shift_factor_y += 1
            refresh(xs, ys)
        elif t == 100: #right
            shift_factor_x += 1
            refresh(xs, ys)
        elif t == 115: #down
            shift_factor_y -= 1
            refresh(xs, ys)
        elif t == 113: # q
            cv2.destroyWindow("Image")
            break_flag = True
            break

def refresh(xs, ys):
    global img, shift_factor_x, shift_factor_y

    disp_xs = np.add(xs, shift_factor_x)
    disp_ys = np.add(ys, shift_factor_y)

    img = gen_fig_array(disp_xs, disp_ys)
    cv2.destroyWindow("Image")
    cv2.imshow("Image", img)

def gen_fig_array(xs, ys):
    global master_xs, master_ys

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111)

    ax.scatter(master_xs, master_ys, color='black')
    ax.scatter(xs, ys, color='blue') 
    ax.axis([-25, 0, 0, 15])

    fig.tight_layout()
    fig.set_size_inches(10, 10)

    ret = figure_to_array(fig)
    plt.close(fig)
    return ret