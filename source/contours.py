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

    print("accum", accum)

    for pt in contour[:,0,:]:
        pt[1] -= accum 
        pt[1] += 350
    
    return contour

def scale_contour(contour, scale_factor=1):
    for pt in contour[:,0,:]:
        pt[0] *= scale_factor
        pt[1] *= scale_factor
    return contour

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
    rotated_contour = rotated_contour.astype(np.int32)

    return rotated_contour

def extract_data(contour):
    xs = []
    ys = []

    for i in range(0, len(contour[:,0,:])):
        xs += [contour[i, 0, 0]]
        ys += [-1 * contour[i, 0, 1]]

    return xs, ys

def process_contour(img, pts, scale, scale_factor, angle, FAT_DEPTH):
    initial_contour = np.array(pts).reshape((-1, 1, 2)).astype(np.int32)

    # Reduces noise on contour 
    smooth_contours = smooth_contour([initial_contour])

    # Finds distance transform of drawn contour
    new_size = (img.shape[0] + 500, img.shape[1] + 500, img.shape[2] + 0)
    temp = np.ones(new_size,dtype=np.uint8)
    cv2.drawContours(temp, smooth_contours, 0, (0, 0, 0))
    temp = cv2.cvtColor(temp, cv2.COLOR_BGR2GRAY)
    dist = cv2.distanceTransform(temp, cv2.DIST_L2, cv2.DIST_MASK_PRECISE)

    # Finds contour with a specified fat thickness  
    b = int(FAT_DEPTH/scale) - 0.5
    t = int(FAT_DEPTH/scale) + 0.5
    ring = cv2.inRange(dist, b, t)
    expanded_contours, hierarchy = cv2.findContours(ring, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    expanded_contour = expanded_contours[2]

    cv2.drawContours(img, smooth_contours, 0, (255, 255, 0))
    cv2.drawContours(img, expanded_contours, 2, (0, 0, 255), 2)

    # Scales and rotates contour to normalize across pictures 
    expanded_contour = rotate_contour(expanded_contour, -angle + 180)
    expanded_contour = scale_contour(expanded_contour, scale_factor)  
    expanded_contour = crop_top(expanded_contour)
    expanded_contour = shift_left(expanded_contour)
    expanded_contour = shift_up(expanded_contour)

    return expanded_contour