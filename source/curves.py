import math
import time

from scipy.optimize import curve_fit
from scipy import stats
from scipy.integrate import quad
import matplotlib.pyplot as plt 
import numpy as np
from tqdm import tqdm

def fit_curve(xs, ys):
    print("Fitting curve to data...\nThis may take a while.")
    start = time.time()
    # params = np.polyfit(xs, ys, 8)    
    params, _ = curve_fit(func, xs, ys)
    print("Curve fit with parameters\n", params, "in", round(time.time() - start, 2), "seconds")
    return params

def func(x, a, b):#, c, d, f, g, h, i):
    # fun = np.polyval([a, b, c, d, e, f], x)*x*(x+3.1415)
    # fun = a*(x**8)/8 + 3.1415*a*(x**7)/7 + b*(x**7)/7 + 3.1415*b*(x**6)/6 + c*(x**6)/6 + 3.1415*c*(x**5)/5 + d*(x**5)/5 + \
        # 3.1415*d*(x**4)/4 + e*(x**4)/4 + 3.1415*e*(x**3)/3 + f*(x**3)/3 + 3.1415*f*(x**2)/2 + g

    # fun = (a*x**7+b*x**6+c*x**5+d*x**4+f*x**3+g*x**2+h*x)*(x+37*pi/45)
    # fun = a*x**8/8+b*x**7/7+c*x**6/6+d*x**5/5+f*x**4/4+g*x**3/3+h*x**2/2+i
    # p = 37 * math.pi/45
    
    # fun = a*x**9/9+p*a*x**8/8+b*x**8/8+p*b*x**7/7+c*x**7/7+p*c*x**6/6+d*x**6/6+p*d*x**5/5+f*x**5/5+p*f*x**4/4+g*x**4/4+p*g*x**3/3+h*x**3/3+p*h*x**2/2+i
    fun = a*x**2+b
    
    return fun

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

def graph_data(xs, ys, xs2, ys2, fitparams, fit2):
    x = np.linspace(-4, 1, 1000)
    # y = func(x, fitparams[0], fitparams[1], fitparams[2], fitparams[3], fitparams[4], fitparams[5], fitparams[6], fitparams[7])
    # y2 = func(x, fit2[0], fit2[1], fit2[2], fit2[3], fit2[4], fit2[5], fit2[6], fit2[7])
    y = func(x, fitparams[0], fitparams[1])
    y2 = func(x, fit2[0], fit2[1])

    fig = plt.figure(figsize=(16,8))
    ax = fig.add_subplot(121)
    ax.plot(x, y, c="pink", linewidth=1)
    ax.plot(x, y2, c="red", linewidth=5)
    ax.scatter(xs, ys, s=0.1, c="lightblue")
    ax.scatter(xs2, ys2, s=0.5, c="black")
    ax.scatter([-math.pi*37/45, 0], [12.426, 10.16], c="black", s=45)
    ax.axis([-4, 1, -10, 50])

    ax2 = fig.add_subplot(122, polar=True)
    ax2.plot(x, y, c="pink", linewidth=1)
    ax2.plot(x, y2, c="red", linewidth=5)
    ax2.scatter(xs, ys, c="lightblue",s=0.1)
    ax2.scatter(xs2, ys2, c="black",s=0.5)
    ax2.scatter([-math.pi*37/45, 0], [12.426, 10.16], c="black", s=45)
    ax2.axis([-math.pi, 0, 0, 20])

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
            ret_rs += [rs[i] + val - mean]
            ret_thetas += [thetas[i]]

    # return polar_to_cartesian(ret_thetas, ret_rs)
    return np.deg2rad(ret_thetas), ret_rs


def find_radial_mean(thetas, rs, dtheta=1):
    if (360 % dtheta != 0):
        print("ERR: dtheta must divide 360.")
        return [], []

    print("Averaging data...")

    thetas, rs = sort_data(thetas, rs)
    thetas = np.rad2deg(thetas)

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