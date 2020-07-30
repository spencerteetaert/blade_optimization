import math
import time

from scipy.optimize import curve_fit
from scipy import stats
import matplotlib.pyplot as plt 
import numpy as np
from tqdm import tqdm

# from quicksort import quickSort

def func(x, params):
    return params[0] * x**8 + params[1] * x**7 + params[2] * x**6 + params[3] * x**5 + params[4] * x**4 + params[5] * x**3 + params[6] * x**2 + params[7] * x + params[8]

def func2(x, params):
    return (params[0] * x**8 + params[1] * x**7 + params[2] * x**6 + params[3] * x**5 + params[4] * x**4 + params[5] * x**3 + params[6] * x**2 + params[7] * x + params[8])**0.5

def poly(x, d, e, f, g, h, i, j, k, l):
    return d*x**8 + e*x**7 + f*x**6 + g*x**5 + h*x**4 + i*x**3 + j*x**2 + k*x + l

def fit_curve(xs, ys):
    print("Fitting curve to data...\nThis may take a while.")
    start = time.time()
    data = np.concatenate((xs, ys), axis=0)
    ret = np.reshape(data, (-1, 2), 'F')
    np.sort(ret)

    popt, pcov = curve_fit(poly, ret[:,0], ret[:,1])
    print("Curve fit with parameters\n", popt, "in", time.time() - start, "seconds")
    return popt

def sort_data(xs, ys):
    temp = np.concatenate((xs, ys), axis=0)
    temp = np.reshape(temp, (-1, 2), 'F')
    i = np.argsort(xs)
    return temp[i,0], temp[i,1]

def polar_to_cartesian(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def cartesian_to_polar(x, y):
    theta = np.arctan2(y, x)
    r = np.hypot(x, y)
    return theta, r

def graph_data_cartesian(xs, ys, fitparams):
    # x = np.linspace(np.min(xs), np.max(xs), 1000)
    # y = func(x, fitparams)

    m = max(2*np.max(xs), -1*np.min(ys))

    plt.rcParams["figure.figsize"] = (8,8)
    # plt.plot(x, y, c="red", linewidth=5)
    plt.scatter(xs, ys, s=1)
    plt.axis([0, 25, 0, 25])
    plt.show()

def graph_data_polar(thetas1, rs1, thetas2, rs2, fitparams, fit2):
    # t = np.linspace(np.min(thetas1), np.max(thetas1), 1000)
    # r = func(t, fitparams)
    # r2 = func(t, fit2)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)

    # ax.rcParams["figure.figsize"] = (8,8)
    # plt.polar(t, r, c="pink", linewidth=1)
    # plt.polar(t, r2, c="red", linewidth=5)
    ax.scatter(thetas1, rs1, c="lightblue",s=2)
    ax.scatter(thetas2, rs2, c="red",s=5)
    ax.axis([-math.pi, 0, 0, 12])
    plt.show()

def deviate(thetas, rs, percentile, dtheta=1):
    print("Deviating data...")

    thetas, rs = sort_data(thetas, rs)
    thetas = np.rad2deg(thetas)

    ret_thetas = []
    ret_rs = []

    other_index = 0

    print("\tRunning deviation algorithm. This may take a while.")
    for i in tqdm(range(0, len(thetas))):
        theta = thetas[i]

        #Set sweep bounds
        lb = theta - dtheta/2
        ub = theta + dtheta/2
        in_wedge_thetas = []
        in_wedge_rs = []
        count = 0

        #Forward sweep 
        other_index = i + 1
        while True:
            if (other_index >= len(thetas)):
                break
            if (thetas[other_index] < lb or thetas[other_index] >= ub):
                break
            in_wedge_rs += [rs[other_index]]
            in_wedge_thetas += [thetas[other_index]]
            count += 1
            other_index += 1
        
        #Backward sweep
        other_index = i - 1
        while True:
            if (other_index < 0):
                break
            if (thetas[other_index] < lb or thetas[other_index] >= ub):
                break
            in_wedge_rs += [rs[other_index]]
            in_wedge_thetas += [thetas[other_index]]
            count += 1
            other_index -= 1
        
        if count != 0:
            mean = np.mean(in_wedge_rs)
            val = stats.scoreatpercentile(in_wedge_rs, percentile)
            ret_rs += list(np.add(in_wedge_rs, val - mean))
            ret_thetas += in_wedge_thetas

    # return polar_to_cartesian(ret_thetas, ret_rs)
    return np.deg2rad(ret_thetas), ret_rs


def find_radial_mean(thetas, rs, dtheta=1):
    if (360 % dtheta != 0):
        print("ERR: dtheta must divide 360.")
        return [], []

    print("Averaging data...")

    thetas, rs = sort_data(thetas, rs)
    thetas = np.rad2deg(thetas)

    print("THETAS", thetas)
    print("RS", rs)

    ret_thetas = []
    ret_rs = []

    index = 0

    print("\tRunning mean generating algorithm. This may take a while.")
    for theta in range(-340, -20, dtheta):
        #Set sweep bounds
        lb = theta - dtheta/2
        ub = theta + dtheta/2
        # in_wedge_thetas = []
        in_wedge_rs = []
        count = 0

        #Forward sweep 
        while True:
            if (index >= len(thetas)):
                break
            if (thetas[index] < lb or thetas[index] >= ub):
                break
            in_wedge_rs += [rs[index]]
            # in_wedge_thetas += [thetas[index]]
            count += 1
            index += 1
        
        if count != 0:
            
            # mean = np.mean(in_wedge_rs)
            mean = stats.scoreatpercentile(in_wedge_rs, 50)
            print(lb, ub, mean, min(in_wedge_rs), max(in_wedge_rs))
            ret_rs += [mean]
            ret_thetas += [theta]

    # return polar_to_cartesian(ret_thetas, ret_rs)
    return np.deg2rad(ret_thetas), ret_rs