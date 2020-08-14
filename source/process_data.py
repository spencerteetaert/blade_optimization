import copy
import time
import math

import numpy as np

from . import curves
from . import contours
from .data_io import load_data
from .alignment import align_data

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data\GOOD.csv"

def main(data_path=DATA_PATH):
    FAT_DEPTH = 1.2 # cm, the desired fat depth along the loin sw
    FAT_DEPTH_SECONDARY = 2.0 # cm, the desired fat depth along the secondary muscle 
    MEASUREMNET_DECMINAL_POINTS = 2
    SCALE_FACTOR = 10**MEASUREMNET_DECMINAL_POINTS
    

    resultant_xs = []
    resultant_ys = []
    resultant_indices = []

    image_data, loaded_xs, loaded_ys, indices, alignment_points = load_data(data_path)
    pts = [[loaded_xs[i], loaded_ys[i]] for i in range(0, len(loaded_xs))]

    # Scales points to gain resolution with contour functions 
    # pts = contours.scale_pts(pts, SCALE_FACTOR)
    pts = np.array(pts)

    # Expand contour for each curve
    for i in range(0, len(indices)):    
        if i + 1 < len(indices):
            pts_x, pts_y = pts[indices[i]:indices[i+1],0], pts[indices[i]:indices[i+1],1]
        else:
            pts_x, pts_y = pts[indices[i]:len(pts),0], pts[indices[i]:len(pts),1]

        pts_x, pts_y = curves.sort_data(pts_x, pts_y)
        # contour = contours.pts2_to_contour(pts_x, pts_y)

        # don't expand -- done in labelling script 
        # smoothed_contour = contours.smooth_contour(contour)
        # expanded_contour = contours.crop_top(smoothed_contour)

        # Scales contours back to real sizes (cm) 
        # expanded_pts = contours.contour_to_pts(contour)
        # expanded_pts = contours.scale_pts(expanded_pts, 1/SCALE_FACTOR)

        #Flipping the x axis rights the orientation. It is not done earlier 
        #as all the transformations had to happen with positive indices to
        #allow for use in np arrays.
        resultant_indices += [len(resultant_xs)]
        # resultant_xs += list(-1*expanded_pts[:,0]) 
        # resultant_ys += list(expanded_pts[:,1])
        resultant_xs += list(pts_x)
        resultant_ys += list(-1*pts_y)

    # Opens a window to manually align data for shape alignment 
    resultant_xs, resultant_ys = align_data(resultant_xs, resultant_ys, resultant_indices, alignment_points)

    # curves.graph_cartesian(resultant_xs, resultant_ys, [10, 35, -35, -10])

    # Centers data below the 0° axis 
    shift_factor = min(resultant_ys) + 12.3
    resultant_ys = np.add(resultant_ys, -1*shift_factor) 

    # curves.graph_cartesian(resultant_xs, resultant_ys, [10, 35, -25, 0])

    # Converts gathered data to polar (reduces error on blade edges)
    thetas, rs = curves.cartesian_to_polar(resultant_xs, resultant_ys)

    # Generates a percentile expansion for the data 
    thetas2 = copy.deepcopy(thetas)
    rs_deviated = copy.deepcopy(rs)
    thetas2, rs_deviated = curves.deviate(thetas2, rs_deviated, 99, 3)
    # thetas_mean, rs_mean = curves.find_radial_mean(thetas2, rs_deviated, 5)

    # Adds 100 points on gemoetric constraints to force a fita
    thetas2 = np.concatenate((thetas2, np.multiply(np.ones([100000,]),-math.pi*8/45)))
    thetas2 = np.concatenate((thetas2, np.multiply(np.ones([100000,]),-math.pi)))
    rs_deviated = np.concatenate((rs_deviated, np.multiply(np.ones([100000,]), 12.43)))
    rs_deviated = np.concatenate((rs_deviated, np.multiply(np.ones([100000,]), 10.16)))

    # Fits custom function to data
    fit = curves.fit_curve(thetas, rs)
    fit2 = curves.fit_curve(thetas2, rs_deviated)

    # Graphs curve resultdddwd
    curves.graph_data(thetas, rs, thetas2, rs_deviated, fit, fit2)