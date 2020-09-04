import math
import copy
import threading
import time
import glob
import csv

import cv2
import numpy as np
import matplotlib.pyplot as plt

from .label_images import scale_img
from .curves import polar_to_cartesian
from .contours import rotate_points
from . import window

FLIP_BLADE = False

rulers = []
mousedown = (0, 0)
mousedown_ = False
current_mouse_pos = (0, 0)

scale = 1
shift_factor_x = 0
shift_factor_y = 0

break_flag = False

img = 0
output = None

xs, ys = [], []

def gen_curve_disp():
    global xs, ys, scale
    params = [float(window.fit_params[i].get()) for i in range(0, 12)]
    strip_trailing(params)

    print("PARAMS", params)

    thetas = np.linspace(-math.pi, -8/45*math.pi, 1000)
    rs = np.polyval(params, thetas)
    xs, ys = polar_to_cartesian(thetas, rs)
    xs, ys = rotate_points(xs, ys, 180)
    xs = np.multiply(xs, 1/scale) # Scale to new
    ys = np.multiply(ys, 1/scale)

def strip_trailing(a):
    for i in range(len(a) - 1, -1, -1):
        if a[i] != 0:
            break
    del a[i+1:]

def draw(img, sx, sy):
    global xs, ys
    global scale
    global rulers, mousedown, mousedown_, current_mouse_pos

    ret = copy.deepcopy(img)
    iH, iW, _ = ret.shape

    current_mag = ((mousedown[0] - current_mouse_pos[0])**2 + (mousedown[1] - current_mouse_pos[1])**2)**0.5 * scale
    font = cv2.FONT_HERSHEY_SIMPLEX

    #Draws curve
    for i in range(0, len(xs)):
        ret[min(iH-1, max(int(ys[i] + sy), 0)), min(iW-1, max(int(xs[i] + sx), 0))] = (255, 255, 255)

    #Draws all scale lines and length measurements
    if len(rulers) > 0:
        cv2.line(ret, (rulers[0][0][0], rulers[0][0][1]), (rulers[0][1][0], rulers[0][1][1]), (255, 255, 255), 3)
        cv2.putText(ret, str(round(((rulers[0][0][0] - rulers[0][1][0])**2 + (rulers[0][0][1] - rulers[0][1][1])**2)**0.5 * scale, 2)) \
            + "cm", (rulers[0][0][0], rulers[0][0][1]), font, 0.6, (0,0,0))
    for i in range(1, len(rulers)):
        cv2.line(ret, (rulers[i][0][0] + sx, rulers[i][0][1] + sy), (rulers[i][1][0] + sx, rulers[i][1][1] + sy), (255, 0, 255), 3)
        cv2.putText(ret, str(round(((rulers[i][0][0] - rulers[i][1][0])**2 + (rulers[i][0][1] - rulers[i][1][1])**2)**0.5 * scale, 2)) \
            + "cm", (rulers[i][0][0] + sx, rulers[i][0][1] + sy), font, 0.6, (0,0,0))

    #Draws line currently being placed 
    if mousedown_:
        colour = (255, 0, 255) if len(rulers) > 0 else (255, 255, 255)
        cv2.line(ret, (mousedown[0] + sx, mousedown[1] + sy), (current_mouse_pos[0] + sx, current_mouse_pos[1] + sy), colour, 2)
        to_write = str(round(current_mag, 2)) if len(rulers) > 0 else str(window.known_length.get())
        cv2.putText(ret, "Line length:" + to_write + "cm", (mousedown[0] + sx, mousedown[1] + sy), font, 0.6, (0,0,0))

    return ret

def display():
    global FLIP_BLADE, break_flag
    global xs, ys
    global img, output
    global shift_factor_x, shift_factor_y, scale
    global rulers

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouse_event)

    while True:
        t = cv2.waitKeyEx(1)
        # print(t)

        #Fine control 
        if t == 2424832: #left
            shift_factor_x -= 1
        elif t == 2490368: #up 
            shift_factor_y -= 1
        elif t == 2555904: #right
            shift_factor_x += 1
        elif t == 2621440: #down
            shift_factor_y += 1

        #Coarse control
        elif t == 119: #w 
            shift_factor_y -= 5
        elif t == 97: #a
            shift_factor_x -= 5
        elif t == 115: #s
            shift_factor_y += 5
        elif t == 100: #d
            shift_factor_x += 5

        elif t == 101: #e -- flip blade
            FLIP_BLADE = True
        elif t == 8: #BACKSPACE 
            rulers = rulers[:-1]

        elif t == 32: #SPACE -- next image
            cv2.destroyWindow("Image")
            break
        elif t == 113: # q -- quit
            cv2.destroyWindow("Image")
            break_flag = True
            break

        if FLIP_BLADE:
            FLIP_BLADE = False
            xs = np.multiply(xs, -1) #flips blade for left bellies 

        output = draw(img, shift_factor_x, shift_factor_y)

        cv2.imshow("Image", output)

def mag(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def mouse_event(event, pX, pY, flags, param):
    global xs, ys
    global shift_factor_x, shift_factor_y, scale
    global rulers, mousedown, mousedown_, current_mouse_pos
    
    current_mouse_pos = (pX - shift_factor_x, pY - shift_factor_y)

    if event == cv2.EVENT_LBUTTONUP:
        mousedown_ = False
        print("Clicked at", pX, pY)
        if len(rulers) == 0:
            rulers = [[(mousedown[0] + shift_factor_x, mousedown[1] + shift_factor_y), (pX, pY)]]

            xs = np.multiply(xs, scale) # Scale back to normal
            ys = np.multiply(ys, scale)

            scale = window.known_length.get() / mag((mousedown[0] + shift_factor_x, mousedown[1] + shift_factor_y), (pX, pY)) # cm/px
            
            xs = np.multiply(xs, 1/scale) # Scale to new
            ys = np.multiply(ys, 1/scale)
        elif len(rulers) > 0:
            rulers += [[mousedown, (pX - shift_factor_x, pY - shift_factor_y)]]
            
    elif event == cv2.EVENT_LBUTTONDOWN:
        mousedown_ = True
        mousedown = (pX - shift_factor_x, pY - shift_factor_y)
            
def main(image_folder, data_type, output_folder):
    global break_flag
    global shift_factor_x, shift_factor_y
    global img, output
    global rulers

    path = image_folder + "\*." + data_type
    images = glob.glob(path)

    for i in range(0, len(images)):
        print(images[i])
        img = cv2.imread(images[i])
        img = scale_img(img)
        
        iH, iW, _ = img.shape
        shift_factor_x = int(iW / 2)
        shift_factor_y = int(iH / 4)
        gen_curve_disp()

        t = threading.Thread(target = display, args=[])
        t.daemon = True
        t.start()
        t.join()

        if break_flag:
            break

        rulers = []
    
        if window.save_toggle.get():
            filename = output_folder + "\\" + images[i][-12:]
            cv2.imwrite(filename, output)
            print("Saved file to",filename)