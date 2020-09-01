import math
import time
from textwrap import wrap

from scipy.optimize import curve_fit
from scipy import stats
from scipy.integrate import quad
from matplotlib.pyplot import figure, show, tight_layout
import numpy as np
from tqdm import tqdm

polynomial_degree = 7

def func(x, a=0, b=0, c=0, d=0, e=0, f=0, g=0, h=0, i=0, j=0, k=0, l=0, m=0):
    global polynomial_degree
    args = [a, b, c, d, e, f, g, h, i, j, k, l, m]
    params = [args[i] for i in range(0, polynomial_degree+1)]
    fun = np.polyval(params, x)
    return fun
def func_for_graph(x, *args):
    global polynomial_degree
    print("ARGS",args)
    params = [args[0][i] for i in range(0, polynomial_degree+1)]
    fun = np.polyval(params, x)
    return fun

def fit_curve(xs, ys):
    global polynomial_degree
    start = time.time()
    params, _ = curve_fit(func, xs, ys)
    print("Curve fit with parameters\n", params, "in", round(time.time() - start, 2), "seconds.")
    return params

def polar_to_cartesian(theta, r):
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    return x, y

def cartesian_to_polar(x, y):
    theta = np.arctan2(y, x)
    r = np.hypot(x, y)
    return theta, r

def sort_data(xs, ys):
    '''
        Given a set of both xs and ys, sorts the data 
        according to ascending x value without breaking
        up the x-y pairs 
    '''
    temp = np.concatenate((xs, ys), axis=0)
    temp = np.reshape(temp, (-1, 2), 'F')
    i = np.argsort(xs)
    return temp[i,0], temp[i,1]

def graph_data(xs, ys, xs2, ys2, fitparams, fit2):
    global polynomial_degree
    x = np.linspace(-3.1415, -0.5585, 1000)
    y = func_for_graph(x, fitparams)
    y2 = func_for_graph(x, fit2)

    fig = figure(figsize=(8,6))

    ax = fig.add_subplot(111, polar=True)

    title = "Fit Polynomial: \nr = "
    for i in range(0, polynomial_degree):
        title += str(round(fit2[i], 3))
        title += "Θ^"
        title += str(polynomial_degree-i)
        title += " + "
    title += str(round(fit2[polynomial_degree], 3))

    ax.set_title("\n".join(wrap(title, 50)))
    ax.plot(x, y, c="pink", linewidth=1)
    ax.plot(x, y2, c="red", linewidth=3)
    ax.scatter(xs, ys, c="lightblue",s=0.5)
    ax.scatter(xs2, ys2, c="black",s=0.5)
    # Adds physical constraint markers
    ax.scatter([-math.pi*8/45, -math.pi], [12.426, 10.16], c="black", s=45)

    ax.axis([-math.pi, 0, 0, 20])

    tight_layout()
    show()

def graph_cartesian(xs, ys, bounds):
    fig = figure(figsize=(8,8))
    ax = fig.add_subplot(111)
    ax.scatter(xs, ys, s=0.5, c="lightblue")
    ax.axis(bounds)

    show()

def deviate(thetas, rs, percentile, dtheta=1):
    '''
        Extends the data to the <percentile> percentile. 
        Given a set of data (thetas and rs) that make up
        the ideal cut lines for multiple loins, this 
        function returns the r values associated with 
        the <percentile> percentile of loins. 

        thetas ==> list of theta values
        rs ==> list of r values 
        percentile ==> percentile of loins you wish to capture
        dtheta ==> the sweep size of interest when looking
            for the percentile value. e.g. if dtheta = 1, 
            for each point the algorithm will take the
            <percentile> percentile of the r values within
            ±0.5° of the current theta value. 
    '''
            
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
            ret_rs += [val]
            ret_thetas += [thetas[i]]

    return np.deg2rad(ret_thetas), ret_rs