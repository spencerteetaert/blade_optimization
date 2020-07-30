import numpy as np

xs = [5,7,4,1,2]
ys = [6, 3, 8, 9, 10]

temp = np.concatenate((xs, ys), axis=0)
temp = np.reshape(temp, (-1, 2), 'F')
i = np.argsort(xs)
temp = temp[i,:]


def sort_data(xs, ys):
    temp = np.concatenate((xs, ys), axis=0)
    temp = np.reshape(temp, (-1, 2), 'F')
    i = np.argsort(xs)
    return temp[i,0], temp[i,1]


xs = [5,7,4,1,2]
ys = [6, 3, 8, 9, 10]

xs, ys = sort_data(xs, ys)

print(xs, ys)
print("\n\n\n")

print(np.ones([100,]))
print(np.multiply(np.ones([100,]),-180))
temp = np.multiply(np.ones([100,]),-180)
print(np.concatenate((temp, temp)))
# np.concatenate(thetas, np.multiply(np.ones([100,]),-180))