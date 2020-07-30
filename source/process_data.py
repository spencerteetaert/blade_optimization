import copy
import time

import numpy as np

import curves
import contours as c
from data_io import load_data
from alignment import align_data

FAT_DEPTH = 1.2 # cm, the desired fat depth along the loin sw
FAT_DEPTH_SECONDARY = 2.0 # cm, the desired fat depth along the secondary muscle 
MEASUREMNET_DECMINAL_POINTS = 2
SCALE_FACTOR = 10**MEASUREMNET_DECMINAL_POINTS
DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data\loin_data-20200730-115426.csv"

resultant_xs = []
resultant_ys = []
resultant_indices = []

header, image_data, loaded_xs, loaded_ys, indices = load_data(DATA_PATH)
pts = [[loaded_xs[i], loaded_ys[i]] for i in range(0, len(loaded_xs))]

# Scales points to gain resolution with contour functions 
pts = c.scale_pts(pts, SCALE_FACTOR)

# Expand contour for each curve
for i in range(0, len(indices)):    
    if i + 1 < len(indices):
        contour = np.array(pts[indices[i]:indices[i+1]]).reshape((-1, 1, 2)).astype(np.int32)
    else:
        contour = np.array(pts[indices[i]:len(pts)]).reshape((-1, 1, 2)).astype(np.int32)

    expanded_contour = c.expand_contour(contour, SCALE_FACTOR, FAT_DEPTH)
    # expanded_contour = c.shift_contour(expanded_contour)
    expanded_contour = c.crop_top(expanded_contour)

    # Scales contours back to real sizes (cm) 
    expanded_pts = np.array(expanded_contour).reshape((-1, 2)).astype(np.float)
    expanded_pts = c.scale_pts(expanded_pts, 1/SCALE_FACTOR)

    #Flipping the x axis rights the orientation. It is not done earlier 
    #as all the transformations had to happen with positive indices to
    #allow for use in np arrays. 
    resultant_indices += [len(resultant_xs)]
    resultant_xs += list(-1*expanded_pts[:,0]) 
    resultant_ys += list(expanded_pts[:,1])

# Opens a window to manually align data for shape alignment 
resultant_xs, resultant_ys = align_data(resultant_xs, resultant_ys, resultant_indices)

# Centers data below the 0° axis 
shift_factor = max(resultant_ys)
resultant_ys -= shift_factor
shift_factor = (max(resultant_xs) + min(resultant_xs))/2
resultant_xs -= shift_factor

# Converts gathered data to polar (reduces error on blade edges)
thetas, rs = curves.cartesian_to_polar(resultant_xs, resultant_ys)

# Adds 100 points on gemoetric constraints to force a fit
thetas = np.concatenate((thetas, np.multiply(np.ones([100,]),-180)))
thetas = np.concatenate((thetas, np.multiply(np.ones([100,]),0)))
rs = np.concatenate((rs, np.multiply(np.ones([200,]),10.16)))

# Generates a percentile expansion for the data 
thetas2 = copy.deepcopy(thetas)
rs_deviated = copy.deepcopy(rs)
thetas2, rs_deviated = curves.deviate(thetas2, rs_deviated, 90, 3)
thetas_mean, rs_mean = curves.find_radial_mean(thetas2, rs_deviated, 5)

# Fits 8 degree polynomial to data
# fit = curves.fit_curve(thetas, rs)
# fit2 = curves.fit_curve(thetas_mean, rs_mean)

# Graphs curve result
curves.graph_data_polar(thetas2, rs_deviated, thetas_mean, rs_mean, 0, 0)