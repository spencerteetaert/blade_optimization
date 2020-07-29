import threading as threading
import math
import glob
import time

import cv2
import numpy as np
import imutils

import contours as c
from data_io import write_data

##########################################
### User Constants -- Edit as required ###
##########################################
IMAGE_FOLDER_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\image data" # Folder where images are located 
IMAGE_DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\example photos.csv" # File (.csv) where image data is kept  
OUTPUT_DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data" # Folder where saved data should be exported to 

DATA_TYPE = ".JPG"
LINE_LENGTH = 10 # cm, length of reference line in image

RESOLUTION = 50.526 #px/cm, the resolution of the display screen 

#########################################
### Program Constants -- Don't change ###
#########################################
IMAGE_FOLDER_PATH += r"\*" + DATA_TYPE
timestr = time.strftime("-%Y%m%d-%H%M%S")
OUTPUT_DATA_PATH += r"\loin_data" + timestr + ".csv"

STATES = {1: "set_length", 2: "set_angle", 3: "choose_points"}
state = STATES[1]

break_flag = False
mouse_down = False
mouseX = 0
mouseY = 0

scale = 0 # cm/px 
angle = 0 # degrees
scale_points = []
angle_points = []
chosen_points = []

xs = []
ys = []
processed_names = []
fit_curves = []

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
    global img, state, scale, angle, mouse_down, mouseX, mouseY, scale_points, angle_points, chosen_points

    if event == cv2.EVENT_LBUTTONUP:
        mouse_down = False
        if state == STATES[1]: # Setting scale 
            scale_points += [[pX, pY]]
            cv2.circle(img, (pX, pY), 1, (255, 0, 255), thickness=2)
            if len(scale_points) == 2:
                cv2.line(img, (scale_points[0][0], scale_points[0][1]), (pX, pY), (255, 0, 255), thickness=1)
                scale = LINE_LENGTH / mag(scale_points[0], scale_points[1])

                print("Image scale:", round(scale, 3), "cm/px")
                state = STATES[2]

        elif state == STATES[2]: # Setting angle 
            angle_points += [[pX, pY]]
            cv2.circle(img, (pX, pY), 1, (255, 0, 0), thickness=2)

            if len(angle_points) == 2:
                cv2.line(img, (angle_points[0][0], angle_points[0][1]), (pX, pY), (255, 0, 0), thickness=1)

                y = angle_points[1][1] - angle_points[0][1]
                x = angle_points[1][0] - angle_points[0][0]
                angle = math.degrees(math.atan(y/x))

                print("Image angle:", round(angle, 3), "°")
                state = STATES[3]
            
        elif state == STATES[3]:
            cv2.circle(img, (pX, pY), 1, (255, 255, 0), thickness=2)
            chosen_points += [[pX, pY]]

    elif state == STATES[2] and mouse_down:
        if event == cv2.EVENT_MOUSEMOVE:
            pass
            # cv2.line(img, (angle_points[0][0], angle_points[0][1]), (pX, pY), (255, 0, 0))

def display():
    global img, break_flag, state, scale_points, angle_points, chosen_points

    cv2.imshow("Image", img)
    cv2.setMouseCallback("Image", mouse_event)
    while True:
        cv2.imshow("Image", img)
        k = cv2.waitKey(1) & 0xFF
        if k == ord('n'):
            cv2.destroyWindow("Image")
            break
        elif k == ord('q'):
            cv2.destroyWindow("Image")
            break_flag = True
            break

        elif k == ord('l'):
            state = "set_length"
            scale_points = []
        elif k == ord('a'):
            state = "set_angle"
            angle_points = []
        elif k == ord('c'):
            state = "choose_points"
            chosen_points = []

names = glob.glob(IMAGE_FOLDER_PATH)
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

    # Scales and rotates image 
    # img = scale_img(img, scale_factor=scale_factor)
    # img = imutils.rotate_bound(img, -angle + 180)
    # cv2.imshow("Scaled",img)
    # cv2.waitKey(0)

    if len(chosen_points) > 2:
        selected_contour = c.adjust_pts(chosen_points, scale, angle)

        # Saves contour data
        x, y = selected_contour[:,0], selected_contour[:,1]
        indices += [len(xs)]
        xs += list(x)
        ys += list(y)

        cv2.destroyAllWindows()

    for j in range(0, len(IMAGE_FOLDER_PATH)):
        if names[i][0] == IMAGE_FOLDER_PATH[j]:
            names[i] = names[i][1:]
    processed_names += [names[i]]

    scale_points = []
    angle_points = []
    chosen_points = []
    state = STATES[1]

write_data(OUTPUT_DATA_PATH, IMAGE_DATA_PATH, processed_names, xs, ys, indices)
# Do something with xs and ys