from random import random, randint, choice
from copy import deepcopy
from math import log


class fwrapper:

    """
    A wrapper for the functions that will be used on function nodes.
    Its member variables are name of the function, the function itself,
    and the number of parameters it takes.
    """
    def __init__(self, function, childcount, name):
        self.function = function
        self.childcount = childcount
        self.name = name


class node:

    """
    The class for function nodes (nodes with children). This is initialized with an
    fwrapper. When evaluate is called, it evaluates the child nodes and then applies
    the function to their results.
    """
    def __init__(self, fw, children):
        self.function = fw.function
        self.name = fw.name
        self.children = children

    def evaluate(self, inp):
        results = [n.evaluate(inp) for n in self.children]
        return self.function(results)

    def display(self, indent=0):
        print((' ' * indent) + self.name)
        for c in self.children:
            c.display(indent + 1)


class paramnode:

    """
    The class for nodes that only return one of the parameters passed to the program.
    Its evaluate method returns the parameter specified by idx.
    """
    def __init__(self, idx):
        self.idx = idx

    def evaluate(self, inp):
        return inp[self.idx]

    def display(self, indent=0):
        print('%sp%d' % (' ' * indent, self.idx))


class constnode:

    """
    Nodes that return a constant value. The evaluate method simply returns the
    value with which in was initialized.
    """
    def __init__(self, v):
        self.v = v

    def evaluate(self, inp):
        return self.v

    def display(self, indent=0):
        print('%s%d' % (' ' * indent, self.v))


# some helper functions

addw = fwrapper(lambda l: l[0] + l[1], 2, 'add')

subw = fwrapper(lambda l: l[0] - l[1], 2, 'substract')

mulw = fwrapper(lambda l: l[0] * l[1], 2, 'multiply')


def iffunc(l):

    if l[0] > 0:
        return l[1]
    else:
        return l[2]


ifw = fwrapper(iffunc, 3, 'if')


def isgreater(l):

    if l[0] > l[1]:
        return 1
    else:
        return 0


gtw = fwrapper(isgreater, 2, 'isgreater')

flist = [addw, mulw, ifw, gtw, subw]  # list of all the functions for random choosing


"""def exampletree():
    return node(ifw, [
        node(gtw, [paramnode(0), constnode(3)]),
        node(addw, [paramnode(1), constnode(5)]),
        node(subw, [paramnode(1), constnode(2)]),
    ])
"""


def makerandomtree(pc, maxdepth=4, fpr=0.5, ppr=0.6):

    """
    This function creates a node with a random function and then looks to see how
    many child nodes this function requires. For every child node required, the
    function calls itself to create a new node.
    :param pc: number of parameters that the tree will take as input
    :param fpr: gives the probability that the new node created will be a function node
    :param ppr: gives that probability that it will be a paramnode if it is not a function node
    """
    if random() < fpr and maxdepth > 0:
        f = choice(flist)
        children = [makerandomtree(pc, maxdepth - 1, fpr, ppr)
                    for i in range(f.childcount)]
        return node(f, children)
    elif random() < ppr:
        return paramnode(randint(0, pc - 1))
    else:
        return constnode(randint(0, 10))


