import random


def color_generator():
    return '#' + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
