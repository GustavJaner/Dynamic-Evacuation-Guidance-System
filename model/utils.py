import random

from config import *


def random_int_to(a):
    r = random.random() * (a + 1) % (a + 1)
    return int(r)


def get_attribute(matrix, attribute, row=-1, column=-1):
    if row < 0 and column < 0:
        return matrix[:, :, indices[attribute]]
    elif row < 0:
        return matrix[:, column, indices[attribute]]
    elif column < 0:
        return matrix[row, :, indices[attribute]]
    else:
        return matrix[row, column, indices[attribute]]


def get_random_1d_neighbor(n, i):
    r = -n
    while i + r < 0 or i + r >= n:
        r = random_int_to(2) - 1
    return i + r
