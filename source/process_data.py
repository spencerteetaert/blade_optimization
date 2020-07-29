import copy
import curves
import contours as c
import numpy as np

from data_io import load_data

FAT_DEPTH = 1.2 # cm, the desired fat depth along the loin 
FAT_DEPTH_SECONDARY = 2.0 # cm, the desired fat depth along the secondary muscle 
MEASUREMNET_DECMINAL_POINTS = 3
SCALE_FACTOR = 10**MEASUREMNET_DECMINAL_POINTS

DATA_PATH = r"C:\Users\User\Documents\Hylife 2020\One Piece Blade Optimization\Program Data\loin_data-20200729-174022.csv"
header, image_data, xs, ys, indices = load_data(DATA_PATH)


pts = [[xs[i], ys[i]] for i in range(0, len(xs))]
contour = c.scale_pts(pts, SCALE_FACTOR)
contour = np.array(pts).reshape((-1, 1, 2)).astype(np.int32)
print(contour)

expanded_contour = c.expand_contour(contour, SCALE_FACTOR, FAT_DEPTH)
print(expanded_contour)
expanded_contour = c.shift_contour(expanded_contour)

print(expanded_contour)

xs = expanded_contour[:,0,0]
ys = expanded_contour[:,0,1]

print(xs)
print(ys)

# Converts gathered data to polar (reduces error on blade edges)
thetas, rs = curves.cartesian_to_polar(xs, ys)
thetas2 = copy.deepcopy(thetas)
rs_deviated = copy.deepcopy(rs)
thetas2, rs_deviated = curves.deviate(rs_deviated, thetas2, 95, 3)

# Fits 8 degree polynomial to data 
fit = curves.fit_curve(thetas, rs)
fit2 = curves.fit_curve(thetas2, rs_deviated)
# fit = curves.fit_curve(xs, ys)

# Graphs curve result
curves.graph_data_polar(thetas, rs, fit, fit2)
# curves.graph_data_cartesian(xs, ys, fit)