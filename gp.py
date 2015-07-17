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


def scorefunction(tree, dataset):
    """
    This function checks every row in dataset, calculating the output from the function
    and comparing it to the real result. It adds up all the diffences, giving lower
    values for better programs.

    Return value 0 indicates that the program got every result correct
    """
    dif = 0
    for data in dataset:
        v = tree.evaluate([data[0], data[1]])
        dif += abs(v - data[2])
    return dif


def getrankfunction(dataset):
    """
    Returns ranking function for a given dataset
    """
    def rankfunction(population):
        scores = [(scorefunction(tree, dataset), tree) for tree in population]
        scores.sort()
        return scores
    return rankfunction


def mutate(tree, pc, probchange=0.1):
    """
    Function begins at the top of the tree and decides whether the node should be
    altered. If not, it calls mutate on the child nodes of the tree.
    """
    if random() < probchange:
        return makerandomtree(pc)
    else:
        result = deepcopy(tree)
        if isinstance(tree, node):
            result.children = [mutate(c, pc, probchange) for c in tree.children]
        return result


def crossover(tree1, tree2, probswap=0.7, top=1):
    """
    This function takes two trees as inputs and traverses down both of them. If a randomly
    selected threshold is reached, the function returns a copy of the first tree with one
    of its branches replaced by a branch in the second tree.
    """
    if random() < probswap and not top:
        return deepcopy(tree2)
    else:
        result = deepcopy(tree1)
        if isinstance(tree1, node) and isinstance(tree2, node):
            result.children = [crossover(c, choice(tree2.children), probswap, 0)
                            for c in tree1.children]
        return result


def evolve(pc, popsize, rankfunction, maxgen=500, mutationrate=0.1, breedingrate=0.4,
           pexp=0.7, pnew=0.05):
    """
    Function returns a random number, tending towards lower numbers. The lower pexp is,
    more lower numbers you will get

    :param rankfunction: function used on the list of programs to rank them from best to worst
    :param mutationrate: probability of a mutation, passed on to mutate
    :param breedingrate: probability of crossover, passed on to crossover
    :param popsize: the size of initial population
    :param pexp: rate of decline in the probability of selecting lower-ranked programs.
                    A higher value makes the selection process more stringent, choosing only
                    programs with the best ranks to repicate
    :param pnew: probability when building the new population that a completely new, random
                    program is introduced
    """

    def selectindex():
        return int(log(random())/log(pexp))

    # creating a random initial population
    population = [makerandomtree(pc) for i in range(popsize)]
    for i in range(maxgen):
        scores = rankfunction(population)
        print(scores[0][0])
        if scores[0][0] == 0:
            break

        # new population from the two best
        newpop = [scores[0][1], scores[1][1]]
        # building next generation
        while len(newpop) < popsize:
            if random() > pnew:
                newpop.append(mutate(
                    crossover(scores[selectindex()][1],
                              scores[selectindex()][1],
                              probswap=breedingrate),
                    pc, probchange=mutationrate))
            else:
                # just adding random node to mix things up
                newpop.append(makerandomtree(pc))
        population = newpop
    scores[0][1].display()
    return scores[0][1]