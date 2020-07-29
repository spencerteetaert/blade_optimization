import math

from scipy.optimize import curve_fit
from scipy import stats
import matplotlib.pyplot as plt 
import numpy as np

def func(x, params):
    return params[0] * x**8 + params[1] * x**7 + params[2] * x**6 + params[3] * x**5 + params[4] * x**4 + params[5] * x**3 + params[6] * x**2 + params[7] * x + params[8]

def func2(x, params):
    return (params[0] * x**8 + params[1] * x**7 + params[2] * x**6 + params[3] * x**5 + params[4] * x**4 + params[5] * x**3 + params[6] * x**2 + params[7] * x + params[8])**0.5

def poly(x, d, e, f, g, h, i, j, k, l):
    return d*x**8 + e*x**7 + f*x**6 + g*x**5 + h*x**4 + i*x**3 + j*x**2 + k*x + l

def fit_curve(xs, ys):
    xs, ys = sort_data(xs, ys)
    popt, pcov = curve_fit(poly, xs, ys)
    
    return popt

def sort_data(xs, ys):
    for i in range(0, len(xs) - 1):
        flag = False
        for j in range(0, len(xs) - 1):
            if xs[j] > xs[j + 1]:
                flag = True
                xs[j], xs[j+ 1] = xs[j + 1], xs[j]
                ys[j], ys[j+ 1] = ys[j + 1], ys[j]
        if flag == False:
            break

    return xs, ys

def polar_to_cartesian(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def cartesian_to_polar(x, y):
    theta = np.arctan2(y, x)
    r = np.hypot(x, y)
    return theta, r

def graph_data_cartesian(xs, ys, fitparams):
    x = np.linspace(np.min(xs), np.max(xs), 1000)
    y = func(x, fitparams)

    m = max(2*np.max(xs), -1*np.min(ys))

    plt.rcParams["figure.figsize"] = (8,8)
    plt.plot(x, y, c="red", linewidth=5)
    plt.scatter(xs, ys, s=1)
    plt.axis([-m/2, m/2, -m, 0])
    plt.show()

def graph_data_polar(thetas, rs, fitparams, fit2):
    t = np.linspace(np.min(thetas), np.max(thetas), 1000)
    r = func(t, fitparams)
    r2 = func(t, fit2)

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, polar=True)

    # ax.rcParams["figure.figsize"] = (8,8)
    plt.polar(t, r, c="red", linewidth=2)
    plt.polar(t, r2, c="pink", linewidth=3)
    ax.scatter(thetas, rs, s=1)
    ax.axis([-math.pi, 0, 0, 12])
    plt.show()

def deviate(rs, thetas, percentile, dtheta=1):
    thetas, rs = sort_data(thetas, rs)
    thetas = np.rad2deg(thetas)

    ret_thetas = []
    ret_rs = []

    other_index = 0

    for i in range(0, len(thetas)):
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