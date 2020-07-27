import threading as threading
import math
import glob

import cv2
import numpy as np
from scipy.interpolate import splprep, splev

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Opttimization\image data\*.JPG"
LINE_LENGTH = 10 # cm
FAT_DEPTH = 1.2 # cm

STATES = {1: "set_length", 2: "set_angle", 3: "choose_points"}
state = STATES[1]

break_flag = False
mouse_down = False
mouseX = 0
mouseY = 0

scale = 0 # cm/px 
angle = 0 # rad
scale_points = []
angle_points = []
chosen_points = []

def smooth_contour(contours):
    ret = []
    for contour in contours:
        x, y = contour.T

        x = x.tolist()[0]
        y = y.tolist()[0]

        tck, u = splprep([x,y], u=None, s=1.0, per=1)
        u_new = np.linspace(u.min(), u.max(), 75)
        x_new, y_new = splev(u_new, tck, der=0)
        res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new,y_new)]

        ret.append(np.asarray(res_array, dtype=np.int32))
    return ret

def mag(p1, p2):
    return ((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)**0.5

def scale_img(img, width=1000):
    iH, iW, _ = img.shape

    dest_width = width
    dest_height = round((width / iW) * iH)

    res = cv2.resize(img, dsize=(dest_width, dest_height), interpolation=cv2.INTER_CUBIC)
    return res

def mouse_event(event, pX, pY, flags, param):
    global img, state, scale, mouse_down, mouseX, mouseY, scale_points, angle_points, chosen_points

    if event == cv2.EVENT_LBUTTONUP:
        mouse_down = False
        if state == STATES[1]: # Setting scale 
            scale_points += [[pX, pY]]
            cv2.circle(img, (pX, pY), 1, (255, 0, 255), thickness=2)
            if len(scale_points) == 2:
                cv2.line(img, (scale_points[0][0], scale_points[0][1]), (pX, pY), (255, 0, 255), thickness=1)
                scale = LINE_LENGTH / mag(scale_points[0], scale_points[1])

                print("Scale:", round(scale, 3))
                state = STATES[2]

        elif state == STATES[2]: # Setting angle 
            angle_points += [[pX, pY]]
            cv2.circle(img, (pX, pY), 1, (255, 0, 0), thickness=2)

            if len(angle_points) == 2:
                cv2.line(img, (angle_points[0][0], angle_points[0][1]), (pX, pY), (255, 0, 0), thickness=1)

                y = angle_points[1][1] - angle_points[0][1]
                x = angle_points[1][0] - angle_points[0][0]
                angle = math.atan(y/x)

                print("Angle:", round(angle, 3))
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


for name in glob.glob(DATA_PATH):
    print("Analyzing", name)
    img = cv2.imread(name)
    img = scale_img(img)
    # hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    img_h, img_w = img.shape[:2]

    # Creates a new thread with target function 
    t = threading.Thread(target = display, args=[])

    # Sets priority level of thread. Daemon threads do not stop the main
    # program from running and are closed when main is
    t.daemon = True

    #Starts thread
    t.start()
    #Pauses here until thread is completed
    t.join()

    if break_flag:
        break

    if len(chosen_points) > 2:
        initial_contour = np.array(chosen_points).reshape((-1, 1, 2)).astype(np.int32)

        smooth_contours = smooth_contour([initial_contour])

        new_size = (img.shape[0] + 500, img.shape[1] + 500, img.shape[2] + 0)

        print("asd", new_size)
        temp = np.ones(new_size,dtype=np.uint8)
        cv2.drawContours(temp, smooth_contours, 0, (0, 0, 0))
        temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)

        dist = cv2.distanceTransform(temp, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

        b = int(FAT_DEPTH/scale) - 0.5
        t = int(FAT_DEPTH/scale) + 0.5

        ring = cv2.inRange(dist, b, t)
        expanded_contours, hierarchy = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

        cv2.drawContours(img, smooth_contours, 0, (255, 255, 0))
        cv2.drawContours(img, expanded_contours, 2, (0, 0, 255), 2)
        # cv2.drawContours(img, expanded_contours, 0, (0, 255, 0), 2)

        cv2.imshow("Image",img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    scale_points = []
    angle_points = []
    chosen_points = []
    state = STATES[1]