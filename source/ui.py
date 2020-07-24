import threading as threading
import math

import cv2
import numpy as np

'''
    Iterates through images. User clicks on the image to lay a point. 
    When 'n' is pressed, the points are connected and the min/max HSV
    values found within the enclosed space is returned. 
    Images files should be of the form "DATA_PATH<index value>.FILE_TYPE"
    Controls: 
    - press 'q' to quit
    - press 'n' to go to the next image
    - press 'd' to delete the last placed point 
'''

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\Automation\One Piece Blade Opttimization\image data"
state = "set_length"
length_pts = []

class Point(object):
    def __init__(self, x=0,y=0):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

def mouse_event(event, pX, pY, flags, param):
    global img, points, state

    if event == cv2.EVENT_LBUTTONUP:
        if state == "set_length":
            cv2.rectangle(img, (pX - 2, pY - 2), (pX + 2, pY + 2), (0, 255, 200), -1)
            length_pts += [[pX, pY]]

def display():
    global img, i, points, flag, state

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
        elif k == ord('d'):
            points = points[:-1]


for i in range(START_INDEX, END_INDEX+1):
    img = cv2.imread(DATA_PATH+str(i)+FILE_TYPE)
    # temp = cv2.cvtColor(img, cv2.COLOR_YUV2BGR_NV21)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    img_h, img_w = img.shape[:2]
    points = []

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

    if len(points) > 2:
        contour = np.array(points).reshape((-1, 1, 2)).astype(np.int32)

        #finds all pixels inside the drawn contour 
        temp1 = np.array([[0 if cv2.pointPolygonTest(contour, (x,y), False) != 1 else 255 for x in range(0, img.shape[1])] for y in range(0, img.shape[0])], dtype=np.int8)
        temp2 = cv2.bitwise_not(temp1)
        temp2 = cv2.bitwise_and(hsv, hsv, mask=temp2)

        # cv2.drawContours(temp2, [contour], 0, (31, 255, 49), 2)
        # cv2.imshow("Image",temp2)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()