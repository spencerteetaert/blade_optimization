import copy
import time
import math

import numpy as np

from . import curves
from . import contours
from .data_io import load_data
from .alignment import align_data
from . import window

pause_flag = False
thetas = []
rs = []

def main(data_path): 
    global pause_flag, percentile, dtheta, thetas, rs

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

        resultant_indices += [len(resultant_xs)]
        resultant_xs += list(pts_x)
        resultant_ys += list(-1*pts_y)

    # Opens a window to manually align data for shape alignment 
    resultant_xs, resultant_ys = align_data(resultant_xs, resultant_ys, resultant_indices, alignment_points)

    # Centers data below the 0° axis 
    shift_factor = min(resultant_ys) + 12.3
    resultant_ys = np.add(resultant_ys, -1*shift_factor) 

    # curves.graph_cartesian(resultant_xs, resultant_ys, [10, 35, -25, 0])

    # Converts gathered data to polar (reduces error on blade edges)
    thetas, rs = curves.cartesian_to_polar(resultant_xs, resultant_ys)

def find_best_fit():
    global thetas, rs
    # Generates a percentile expansion for the data 
    thetas2 = copy.deepcopy(thetas)
    rs_deviated = copy.deepcopy(rs)
    percentile = float(window.percentile.get())
    dtheta = float(window.dtheta.get())

    thetas2, rs_deviated = curves.deviate(thetas2, rs_deviated, percentile, dtheta)

    # Adds 100 points on gemoetric constraints to force a fita
    thetas2 = np.concatenate((thetas2, np.multiply(np.ones([100000,]),-math.pi*8/45)))
    thetas2 = np.concatenate((thetas2, np.multiply(np.ones([100000,]),-math.pi)))
    rs_deviated = np.concatenate((rs_deviated, np.multiply(np.ones([100000,]), 12.43)))
    rs_deviated = np.concatenate((rs_deviated, np.multiply(np.ones([100000,]), 10.16)))

    # Fits custom function to data
    curves.polynomial_degree = int(window.degree.get())
    fit = curves.fit_curve(thetas, rs)
    fit2 = curves.fit_curve(thetas2, rs_deviated)

    # Graphs curve resultdddwd
    curves.graph_data(thetas, rs, thetas2, rs_deviated, fit, fit2)