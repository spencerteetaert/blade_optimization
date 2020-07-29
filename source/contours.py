from scipy.interpolate import splprep, splev
import numpy as np
import cv2

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

def find_indices(contour):
    left_val = 100000
    right_val = 0
    left_index = 0
    right_index = 0

    for i in range(0, len(contour[:,0,:])):
        if contour[i, 0, 0] < left_val:
            left_val = contour[i, 0, 0]
            left_index = i
        if contour[i, 0, 0] > right_val:
            right_val = contour[i, 0, 0]
            right_index = i

    return left_index, right_index

def crop_top(contour):
    ret = []

    left_index, right_index = find_indices(contour)

    mid_x = (contour[left_index, 0, 0] + contour[right_index, 0, 0])/2
    left_high = contour[left_index, 0, 1]
    right_high = contour[right_index, 0, 1]

    for i in range(0, len(contour[:,0,:])):
        if contour[i, 0, 0] >= mid_x:
            if contour[i, 0, 1] >= right_high:
                ret += [[contour[i, 0, 0], contour[i, 0, 1]]]
        elif contour[i, 0, 1] >= left_high:
            ret += [[contour[i, 0, 0], contour[i, 0, 1]]]

    ret = np.array(ret).reshape((-1, 1, 2)).astype(np.int32)
    return ret

def shift_left(contour):
    left_index, right_index = find_indices(contour)
    shift_factor = contour[left_index, 0, 0] + (contour[right_index, 0, 0] - contour[left_index, 0, 0])/2

    for pt in contour[:,0,:]:
        pt[0] -= shift_factor
    return contour

def shift_up(contour):
    accum = 0
    for pt in contour[:,0,:]:
        accum += pt[1]
    accum /= len(contour)

    for pt in contour[:,0,:]:
        pt[1] -= accum 
        pt[1] += 350
    
    return contour

def scale_contour(contour, scale_factor=1):
    for pt in contour[:,0,:]:
        pt[0] *= scale_factor
        pt[1] *= scale_factor
    print(contour)
    return contour

def scale_pts(pts, scale_factor=1):
    for pt in pts:
        pt[0] *= scale_factor
        pt[1] *= scale_factor
    return pts

def cartesian_to_polar(x, y):
    theta = np.arctan2(y, x)
    r = np.hypot(x, y)
    return theta, r

def polar_to_cartesian(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def rotate_contour(contour, angle):
    M = cv2.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])

    normalized_contour = contour - [cx, cy]
    
    coordinates = normalized_contour[:, 0, :]
    xs, ys = coordinates[:, 0], coordinates[:, 1]
    thetas, rs = cartesian_to_polar(xs, ys)
    
    thetas = np.rad2deg(thetas)
    thetas = (thetas + angle) % 360
    thetas = np.deg2rad(thetas)
    
    xs, ys = polar_to_cartesian(thetas, rs)
    
    normalized_contour[:, 0, 0] = xs
    normalized_contour[:, 0, 1] = ys

    rotated_contour = normalized_contour + [cx, cy]
    print(rotated_contour)
    # rotated_contour = rotated_contour.astype(np.int32)

    return rotated_contour

def adjust_pts(pts, scale, angle):
    '''
        Given a list of selected points, returns the 
        scaled and rotated points. This normalizes 
        across images. 

        pts == pts to be adjusted
        scale == scale of the image (cm/px)
        angle == angle at which the points should be rotated
    '''
    contour = np.array(pts).reshape((-1, 1, 2)).astype(np.int32)

    # Scales and rotates contour to normalize across pictures 
    contour = scale_contour(contour, 10000)    
    contour = rotate_contour(contour, -angle + 180)
    pts = np.array(contour).reshape((-1, 2)).astype(np.float)
    pts = scale_pts(pts, scale/10000)    

    return pts

def expand_contour(contour, scale_factor, expansion):
    '''
        Given a contour of selected points, 
        function smooths, expands, and returns
        expanded contour.

        contour == contour wanting to be expanded 
        scale_factor == scale factor of contour to cm (contour / scale_factor = cm)
        expansion == desired expansion distance in cm
    '''
    print("1:", contour)
    # Smoothes contour and adds resolution 
    contours = smooth_contour([contour])
    
    print("2:", contours)

    # Finds distance transform of drawn contour
    new_size = (int(max(contours[0][:,0,0]) + expansion/scale_factor + 100), int(max(contours[0][:,0,1]) + expansion/scale_factor + 100), 3)
    temp = np.ones(new_size,dtype=np.uint8)
    cv2.drawContours(temp, contours, 0, (0, 0, 0))
    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    dist = cv2.distanceTransform(temp, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

    # Finds contour with a specified fat thickness  
    b = int(expansion/scale_factor) - 0.5
    t = int(expansion/scale_factor) + 0.5
    ring = cv2.inRange(dist, b, t)
    expanded_contours, hierarchy = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    #### Output format of expanded_contours is off. Not sure why.

    print("4:", expanded_contours[0])

    # Find the largest contour (removes chance of inner offset being returned)
    areas = [cv2.contourArea(expanded_contours[i]) for i in range(0, len(expanded_contours))]
    index = areas.index(max(areas))

    print("3:", expanded_contours[index])

    return expanded_contours[index]

def shift_contour(contour):
    # Shifts contour to same location as all others
    # Alter this to adjust alignment between loins
    contour = shift_left(contour)
    contour = shift_up(contour)

    return contour