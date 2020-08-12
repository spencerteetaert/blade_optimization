import math

from scipy import stats
from scipy.interpolate import splprep, splev
import numpy as np
import cv2

def smooth_contour(contour):
    x, y = contour.T

    x = x.tolist()[0]
    y = y.tolist()[0]

    tck, u = splprep([x,y], u=None, s=1.0, per=1)
    u_new = np.linspace(u.min(), u.max(), 75)
    x_new, y_new = splev(u_new, tck, der=0)
    res_array = [[[int(i[0]), int(i[1])]] for i in zip(x_new,y_new)]

    ret = np.asarray(res_array, dtype=np.int32)

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
    '''
        Given a contour, crops the top portion of it that is, 
        every point above the rightmost and leftmost points 
    '''
    ret = []

    left_index, right_index = find_indices(contour)

    mid_x = (contour[left_index, 0, 0] + contour[right_index, 0, 0])/2 
    width = contour[right_index, 0, 0] - contour[left_index, 0, 0]

    left_boundary =  mid_x + width
    right_boundary = mid_x - width

    left_high = contour[left_index, 0, 1]
    right_high = contour[right_index, 0, 1]

    for i in range(0, len(contour[:,0,:])):
        if contour[i, 0, 0] >= right_boundary and contour[i, 0, 1] >= right_high:
            pass
                # ret += [[contour[i, 0, 0], contour[i, 0, 1]]]
        elif contour[i, 0, 0] <= left_boundary and contour[i, 0, 1] >= left_high:
            pass
                # ret += [[contour[i, 0, 0], contour[i, 0, 1]]]
        else:
            ret += [[contour[i, 0, 0], contour[i, 0, 1]]]

    ret = np.array(ret).reshape((-1, 1, 2)).astype(np.int32)
    return ret

def shift_left(contour, alignment_percentile=20):
    # shift_factor = stats.scoreatpercentile(contour[:,0,0], alignment_percentile)
    left_index, right_index = find_indices(contour)
    shift_factor = contour[left_index, 0, 0] + (contour[right_index, 0, 0] - contour[left_index, 0, 0])/2

    for pt in contour[:,0,:]:
        pt[0] -= shift_factor
    return contour

def shift_up(contour, alignment_percentile=10):
    # shift_factor = stats.scoreatpercentile(contour[:,0,1], alignment_percentile)
    shift_factor = np.average(contour[:,0,1])

    for pt in contour[:,0,:]:
        pt[1] -= shift_factor 
    
    return contour

def scale_contour(contour, scale_factor=1):
    for pt in contour[:,0,:]:
        pt[0] *= scale_factor
        pt[1] *= scale_factor
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

def rotate_contour(contour, angle, cx=None, cy=None):
    if cx is None or cy is None:
        # If no rotation point sepcified, rotate around the center of the contour
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
    # rotated_contour = rotated_contour.astype(np.int32)

    return rotated_contour

def rotate_points(xs, ys, angle, cx=None, cy=None):
    points = [[xs[i]*10000, ys[i]*10000] for i in range(0, len(xs))]
    ctr = pts_to_contour(points)
    ctr = sort_contour(ctr)
    rotated_ctr = rotate_contour(ctr, angle, cx*10000, cy*10000)
    ret = contour_to_pts(rotated_ctr)
    return np.divide(ret[:,0], 10000), np.divide(ret[:,1], 10000)

def adjust_pts(pts, scale, angle):
    '''
        Given a list of selected points, returns the 
        scaled and rotated points. This normalizes 
        across images. 

        pts == pts to be adjusted
        scale == scale of the image (cm/px)
        angle == angle at which the points should be rotated
    '''
    # Convert to contour 
    contour = pts_to_contour(pts)

    # Scales and rotates contour to normalize across pictures 
    contour = scale_contour(contour, 10000)    
    contour = rotate_contour(contour, -angle)
    pts = contour_to_pts(contour)
    pts = scale_pts(pts, scale/10000) 

    return pts

def pts2_to_contour(pts_x, pts_y):
    contour = np.array([[[pts_x[i], pts_y[i]]] for i in range(0, len(pts_x))], dtype=np.int32)
    return contour 

def contour_to_pts2(contour):
    pts = np.array(contour).reshape((-1, 2)).astype(np.float)
    return pts[:,0], pts[:,1]

def pts_to_contour(pts):
    contour = np.array(pts).reshape((-1, 1, 2)).astype(np.int32)
    return contour 

def contour_to_pts(contour):
    pts = np.array(contour).reshape((-1, 2)).astype(np.float)
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
    # Smoothes contour and adds resolution 
    contour = smooth_contour(contour)
    # return contour[0] 

    # Finds distance transform of drawn contour
    new_size = (int(max(contour[:,0,1]) + 100), int(max(contour[0][:,0,0]) + 100), 3)
    temp = np.ones(new_size,dtype=np.uint8)
    cv2.drawContours(temp, [contour], 0, (0, 0, 0))
    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    temp = np.pad(temp, int(expansion*scale_factor), constant_values=1)

    dist = cv2.distanceTransform(temp, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)
    
    # Finds contour with a specified fat thickness  
    b = int(expansion*scale_factor) - 0.5
    t = int(expansion*scale_factor) + 0.5
    ring = cv2.inRange(dist, b, t)
    expanded_contours, hierarchy = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # Find the largest contour (removes chance of inner offset being returned)
    areas = [cv2.contourArea(expanded_contours[i]) for i in range(0, len(expanded_contours))]
    index = areas.index(max(areas))

    return expanded_contours[index]

def shift_contour(contour):
    # Shifts contour to same location as all others
    # Alter this to adjust alignment between loins
    contour = shift_left(contour)
    contour = shift_up(contour)

    return contour

def sort_data(xs, ys):
    temp = np.concatenate((xs, ys), axis=0)
    temp = np.reshape(temp, (-1, 2), 'F')
    i = np.argsort(xs)
    return temp[i,0], temp[i,1]

def sort_contour(contour):
    xs, ys = contour_to_pts2(contour)
    xs, ys = sort_data(xs, ys)
    ret = pts2_to_contour(xs, ys)
    return ret