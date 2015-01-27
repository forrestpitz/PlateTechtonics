__author__ = 'fopitz'
from itertools import izip

def clamp(input, min_value, max_value):
    return sorted([min_value, input, max_value])[1]

def tuple_add(xs,ys):
     return tuple(x + y for x, y in izip(xs, ys))