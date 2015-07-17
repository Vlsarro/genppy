from random import random, randint, choice


def hiddenfunction(x, y):
    return x**2 + 2*y + 3*x + 5


def buildhiddenset():
    rows = []
    for i in range(200):
        x = randint(0, 40)
        y = randint(0, 40)
        rows.append([x, y, hiddenfunction(x, y)])
    return rows
