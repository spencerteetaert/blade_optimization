import math

from scipy.optimize import curve_fit
import matplotlib.pyplot as plt 
import numpy as np

def func(x, params):
    return params[0] * x**8 + params[1] * x**7 + params[2] * x**6 + params[3] * x**5 + params[4] * x**4 + params[5] * x**3 + params[6] * x**2 + params[7] * x + params[8]

def funcp(x, params):
    return params[0] * x**7 + params[1] * x**6 + params[2] * x**5 + params[3] * x**4 + params[4] * x**3 + params[5] * x**2 + params[6] * x + params[7]

def derive_func(params):
    ret = []
    for i in range(0, 8):
        ret += [params[i] * (8-i)]
    return ret

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

def graph_data_polar(thetas, rs, fitparams):
    t = np.linspace(np.min(thetas), np.max(thetas), 1000)
    r = func(t, fitparams)

    plt.rcParams["figure.figsize"] = (8,8)
    plt.polar(t, r, c="red", linewidth=5)
    plt.scatter(thetas, rs, s=1)
    plt.axis([-math.pi, 0, 0, 12])
    plt.show()


# def gen_radial_mean(xs, ys, dtheta=1):
#     thetas, rs = cartesian_to_polar(xs, ys)
#     thetas, rs = sort_data(thetas, rs)

#     print(thetas)

#     ret_thetas = []
#     ret_rs = []

#     index = 0

#     for n in range(int(-180/dtheta), 0, dtheta):
#         theta = dtheta * n

#         #Set sweep bounds
#         lb = theta - dtheta/2
#         ub = theta + dtheta/2
#         accum = 0
#         count = 0

#         #Finds index of first valid number 
#         while (thetas[index] < lb):
#             index += 1

#         #Iterates through entire range generating the running average 
#         while (thetas[index] >= lb and thetas[index] < ub):
#             accum += rs[index]
#             count += 1
#             index += 1
        
#         if count != 0:
#             ret_thetas += [theta]
#             ret_rs += [accum / count]

#     # return polar_to_cartesian(ret_thetas, ret_rs)
#     return np.multiply(ret_thetas, math.pi/180), ret_rs