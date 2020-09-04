import threading as threading
import math
import glob
import time
import copy

import cv2
import numpy as np

from . import contours as c
from .data_io import write_data
from . import geometry
from . import window

IMAGE_FOLDER = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\image data\Good Images" # Folder where images are located 
OUTPUT_FOLDER = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data" # Folder where saved data should be exported to 

DATA_TYPE = ".JPG"
LINE_LENGTH = 10 # cm, length of reference line in image

RESOLUTION = 50.526 #px/cm, the resolution of the display screen 

FLIP_IMAGE_TOGGLE = False

STATES = {1: "Setting Length", 2: "Choosing Reference Point", 3: "Choosing Points"}
state = STATES[1]

break_flag = False
mouse_down = (0, 0)
mouse_down_ = False
current_mouse_pos = (0, 0)
mouseX = 0
mouseY = 0
img = 0

display_break_flag = False

scale = 0 # cm/px 
current_fat_thickness = 12
scale_points = []
chosen_points = []
reference_point = [0, 0] 

xs = []
ys = []
processed_names = []
fit_curves = []
reference_points = []

def mag(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def scale_img(img, width=1000, scale_factor=None):
    iH, iW, _ = img.shape

    if scale_factor is None:
        dest_width = width
        dest_height = round((width / iW) * iH)
    else:
        dest_width = int(iW * scale_factor)
        dest_height = int(iH * scale_factor)

    res = cv2.resize(img, dsize=(dest_width, dest_height), interpolation=cv2.INTER_CUBIC)
    return res


def mouse_event(event, pX, pY, flags, param):
    global img, state, scale, mouse_down, mouse_down_, mouseX, mouseY, scale_points, chosen_points, reference_point, current_fat_thickness, current_mouse_pos

    current_mouse_pos = (pX, pY)

    if event == cv2.EVENT_LBUTTONUP:
        mouse_down_ = False
        if state == STATES[1]: # Setting scale 
            scale_points = [mouse_down, [pX, pY]]

            scale = window.known_length.get() / mag(mouse_down, (pX, pY)) # cm/px

            print("Image scale:", round(scale, 3), "cm/px")
            state = STATES[2]

        elif state == STATES[2]: # Setting reference point 
            reference_point = [pX, pY]
            state = STATES[3]
            
        elif state == STATES[3]: # Choosing points
            if mouse_down[0] != pX or mouse_down[1] != pY: 
                to_add = geometry.expand_for_fat([pX, pY], mouse_down, current_fat_thickness/scale)
            else:
                to_add = [pX, pY]
            chosen_points += [to_add]

        mouse_down = []

    elif event == cv2.EVENT_LBUTTONDOWN:
        mouse_down = (pX, pY)
        mouse_down_ = True

def display():
    global img, break_flag, state, scale_points, chosen_points, current_fat_thickness, reference_point, display_break_flag, FLIP_IMAGE_TOGGLE

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouse_event)

    while True:
        current_fat_thickness = float(window.fat_thickness.get())/10
        
        if FLIP_IMAGE_TOGGLE:
            FLIP_IMAGE_TOGGLE = False
            print("Image Flipped.")
            img = cv2.flip(img, 1)
        
        if display_break_flag:
            display_break_flag = False
            cv2.destroyWindow("Image")
            break
        
        canvas = copy.deepcopy(img)
        to_draw = draw(canvas)
        cv2.imshow("Image", to_draw)

        t = cv2.waitKeyEx(1)
        if t == 32: # SPACE
            cv2.destroyWindow("Image")
            break
        elif t == 113: # (Q)uit
            cv2.destroyWindow("Image")
            break_flag = True
            break

        elif t == 114: # (R)eset
            state = STATES[1]
            scale_points = []
            chosen_points = []
            reference_point = [0, 0]

        elif t == 8: # backspace
            if state == STATES[1]:
                scale_points = []
            elif state == STATES[3]:
                if len(chosen_points) == 0:
                    state = STATES[2]
                    reference_point = [0, 0]
                chosen_points = chosen_points[:-1]
            elif state == STATES[2]:
                if reference_point == [0, 0]:
                    state = STATES[1]
                    scale_points = []
                reference_point = [0, 0]

def draw(canvas):
    global state, scale_points, chosen_points, reference_point, current_fat_thickness, current_mouse_pos, mouse_down_, mouse_down

    msg = "Current state:" + state + "\nFat thickness:" + str(round(current_fat_thickness*10)) + "mm"

    font = cv2.FONT_HERSHEY_SIMPLEX
    y0, dy = 30, 18
    for i, line in enumerate(msg.split('\n')):
        y = y0 + i*dy
        try:
            if (line[0] == '\t'):
                cv2.putText(canvas, line[1:], (25, y), font, 0.6, (100,100, 100))
            else:
                cv2.putText(canvas, line, (15, y), font, 0.6, (0, 0, 0))
        except:
            cv2.putText(canvas, line, (15, y), font, 0.6, (0, 0, 0))

    if len(scale_points) >= 2:
        cv2.line(canvas, (scale_points[0][0], scale_points[0][1]), (scale_points[1][0], scale_points[1][1]), (255,255,255),3)

    if mouse_down_:
        if state == STATES[1]:
            cv2.line(canvas, current_mouse_pos, mouse_down, (255,255,255), 2)
        elif state == STATES[3] and current_mouse_pos != mouse_down:
            point = geometry.expand_for_fat(current_mouse_pos, mouse_down, current_fat_thickness/scale)
            point = (int(point[0]), int(point[1]))
            cv2.arrowedLine(canvas, mouse_down, point, (0,0,0), 2)

    for i in range(0, len(chosen_points)):
        cv2.circle(canvas, (int(chosen_points[i][0]), int(chosen_points[i][1])), 3, (0,0,0))

    if reference_point is not [0, 0]:
        cv2.circle(canvas, (int(reference_point[0]), int(reference_point[1])), 3, (0,0,0), 5)

    return canvas

def main(image_folder=IMAGE_FOLDER, data_type=DATA_TYPE, output_folder=OUTPUT_FOLDER):
    global img, break_flag, state, scale_points, chosen_points, current_fat_thickness, reference_point, processed_names, xs, ys, reference_points

    image_folder += r"\*" + data_type
    timestr = time.strftime("-%Y%m%d-%H%M%S")
    output_folder += r"\loin_data" + timestr + ".csv"

    names = glob.glob(image_folder)
    indices = []

    for i in range(0, len(names)):
        # Opens and scales image
        print("Analyzing", names[i])
        img = cv2.imread(names[i])
        img = scale_img(img)

        # Creates a new thread with target function 
        t = threading.Thread(target = display, args=[])
        t.daemon = True
        t.start()
        t.join()

        # Breaks program if user quits
        if break_flag:
            break

        if len(chosen_points) > 2:
            chosen_points += [reference_point]
            selected_contour = c.adjust_pts(chosen_points, scale, 0)
            reference_point = selected_contour[-1]
            selected_contour = selected_contour[:-1]

            # Saves contour data
            x, y = selected_contour[:,0], selected_contour[:,1]
            indices += [len(xs)]
            xs += list(x)
            ys += list(y)
            reference_points += [reference_point]

            cv2.destroyAllWindows()

            for j in range(0, len(image_folder)):
                if names[i][0] == image_folder[j]:
                    names[i] = names[i][1:]
            processed_names += [names[i]]
        else:
            print("ERR: Not enough data points chosen. Image data was not saved.")

        scale_points = []
        reference_point = [0, 0]
        chosen_points = []
        circle_pts = []
        center_pt = []
        state = STATES[1]

    if len(processed_names) > 0:
        write_data(output_folder, processed_names, xs, ys, indices, reference_points)
    else:
        print("No writable data found.")