import threading as threading
import math
import glob
import time
import copy

import cv2
import numpy as np
import imutils

from . import contours as c
from .data_io import write_data
from . import geometry

IMAGE_FOLDER = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\image data\Good Images" # Folder where images are located 
OUTPUT_FOLDER = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data" # Folder where saved data should be exported to 

DATA_TYPE = ".JPG"
LINE_LENGTH = 10 # cm, length of reference line in image

RESOLUTION = 50.526 #px/cm, the resolution of the display screen 

STATES = {1: "Setting Length", 2: "Setting Angle", 3: "Choosing Points", 4: "Choosing Peak"}
state = STATES[1]

break_flag = False
mouse_down = False
mouseX = 0
mouseY = 0
img = 0

scale = 0 # cm/px 
angle = 0 # degrees
current_fat_thickness = 2.0
scale_points = []
angle_points = []
chosen_points = []
peak_point = [0, 0] 

xs = []
ys = []
processed_names = []
fit_curves = []
peak_points = []

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
    global img, state, scale, angle, mouse_down, mouseX, mouseY, scale_points, angle_points, chosen_points, peak_point, current_fat_thickness

    if event == cv2.EVENT_LBUTTONUP:
        if state == STATES[1]: # Setting scale 
            scale_points += [[pX, pY]]
            if len(scale_points) == 2:
                scale = LINE_LENGTH / mag(scale_points[0], scale_points[1])

                print("Image scale:", round(scale, 3), "cm/px")
                state = STATES[4]

        elif state == STATES[4]: # Setting Peak point 
            peak_point = [pX, pY]
            state = STATES[3]
            
        elif state == STATES[3]: # Choosing points
            to_add = geometry.expand_for_fat([pX, pY], mouse_down, current_fat_thickness/scale)
            chosen_points += [to_add]

        mouse_down = []

    elif state == STATES[3]:
        if event == cv2.EVENT_LBUTTONDOWN:
            mouse_down = [pX, pY]

def display():
    global img, break_flag, state, scale_points, angle_points, chosen_points, current_fat_thickness, angle, peak_point

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouse_event)
    while True:
        canvas = copy.deepcopy(img)
        to_draw = draw(canvas)
        cv2.imshow("Image", to_draw)
        t = cv2.waitKeyEx(1)
        # print(t)
        
        if t == 32: # SPACE
            cv2.destroyWindow("Image")
            break
        elif t == 113: # (Q)uit
            cv2.destroyWindow("Image")
            break_flag = True
            break

        elif t == 114: # (R)eset
            state = "Setting Length"
            scale_points = []
            chosen_points = []
            peak_point = [0, 0]
        elif t == 101: # e
            state = "Choosing Peak"
            peak_point = [0, 0]

        elif t == 119: # w
            current_fat_thickness += 0.1
            current_fat_thickness = min(current_fat_thickness, 5)
        elif t == 115: # s
            current_fat_thickness -= 0.1
            current_fat_thickness = max(current_fat_thickness, 0)

        elif t == 97: # a
            angle += 1
        elif t == 100: # d
            angle -= 1

        elif t == 8: # backspace
            if state == STATES[1]:
                scale_points = scale_points[:-1]
            elif state == STATES[2]:
                angle_points = angle_points[:-1]
            elif state == STATES[3]:
                chosen_points = chosen_points[:-1]
            elif state == STATES[4]:
                peak_point = [0, 0]

def draw(canvas):
    global state, scale_points, angle_points, chosen_points, peak_point, current_fat_thickness, angle

    msg = "Current state:" + state + "\nFat thickness:" + str(round(current_fat_thickness*10)) + "mm\n" + "\nAngle:" + str(angle)

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

    for i in range(0, len(scale_points)):
        cv2.circle(canvas, (scale_points[i][0], scale_points[i][1]), 3, (255,255,255))
    if len(scale_points) >= 2:
        cv2.line(canvas, (scale_points[0][0], scale_points[0][1]), (scale_points[1][0], scale_points[1][1]), (255,255,255),3)
        
    for i in range(0, len(angle_points)):
        cv2.circle(canvas, (angle_points[i][0], angle_points[i][1]), 3, (0,255,255))
    if len(angle_points) >= 2:
        cv2.line(canvas, (angle_points[0][0], angle_points[0][1]), (angle_points[1][0], angle_points[1][1]), (0,255,255),1)

    for i in range(0, len(chosen_points)):
        cv2.circle(canvas, (int(chosen_points[i][0]), int(chosen_points[i][1])), 3, (0,0,0))

    if peak_point is not [0, 0]:
        cv2.circle(canvas, (int(peak_point[0]), int(peak_point[1])), 3, (0,0,0), 5)

    if state == STATES[2]:
        ret = imutils.rotate_bound(canvas, -angle)
        return ret
    else:
        return canvas


def main(image_folder=IMAGE_FOLDER, data_type=DATA_TYPE, output_folder=OUTPUT_FOLDER):
    global img, break_flag, state, scale_points, angle_points, chosen_points, current_fat_thickness, angle, peak_point, processed_names, xs, ys, peak_points

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
            chosen_points += [peak_point]
            selected_contour = c.adjust_pts(chosen_points, scale, angle)
            peak_point = selected_contour[-1]
            selected_contour = selected_contour[:-1]

            # Saves contour data
            x, y = selected_contour[:,0], selected_contour[:,1]
            indices += [len(xs)]
            xs += list(x)
            ys += list(y)
            peak_points += [peak_point]

            cv2.destroyAllWindows()

            for j in range(0, len(image_folder)):
                if names[i][0] == image_folder[j]:
                    names[i] = names[i][1:]
            processed_names += [names[i]]
        else:
            print("ERR: Not enough data points chosen. Image data was not saved.")

        scale_points = []
        angle_points = []
        peak_point = [0, 0]
        chosen_points = []
        circle_pts = []
        center_pt = []
        state = STATES[1]

    if len(processed_names) > 0:
        write_data(output_folder, processed_names, xs, ys, indices, peak_points)
    else:
        print("No writable data found.")

if __name__=="__main__":
    main()