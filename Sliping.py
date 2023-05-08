import random
from graphics import *
import time
import matplotlib.pyplot as plt
import numpy as np
from numba import jit
import numpy as np

#randGenome = [random.randrange(0,2) for x in range (2**viewSize)]

#
##
### REMEMBER: ALL ARRAYS MUST BE STORED AS NUMPY ARRAYS 
##
### IF YOU DONT, I WILL CRY
##
### ALSO SOMETIMES YOU DONT HAVE TO MAKE THEM NUMPY ARRAYS (genRanGenome)
##
#

def genStupidArray(n):
    if n == 1:
        return np.array(['0', '1'])
    else:
        shorter_strings = genStupidArray(n-1)
        with_0 = np.array(['0'+b for b in shorter_strings])
        with_1 = np.array(['1'+b for b in shorter_strings])
        all = np.concatenate((with_0,with_1),axis=None)
        return all

def Twenty_Thousand_Leagues_Under_the_Code():
# part one: in which Mendenbar tries to write code and fails
    # chapter one: A Runnaway Strip setup
    length = 100
    world = np.array([None]*length)
    position = 0
    window = None
    trialLength = 100
    # chapter two: The Genomes and Variables
    populationSize = 10 # POPULATION SIZE MUST BE EVEN
    viewSize = 3
    mutation_ = 0.5
    crossover_ = 1.0
    trials = 10
    dummyArray = [(populationSize-x) for x in range(populationSize)]
    
    genomes = np.array([None]*populationSize)
    for x in range(populationSize):
        genomes[x] = genRanGenome(2**viewSize)
    stupidArray = genStupidArray(3)
# part two: in which simorine gives up on the literary references

    # runFor pt.1
    runs = 100 
        # storage stores the best genome and highest fitness of each generation
    fitnessStorage = np.array([None]*runs)
    genomeStorage = np.array([None]*runs)
    for a in range(runs):
        print(f"{a+1} of {runs} trials")
            
        # genNext pt.1
        newGen = np.array([None]*populationSize)
        #print(f"generation started\n current genomes:\n{genomes}")
        # genFitness pt.1
        fitList = np.array([None]*populationSize)
        for b in range(populationSize):
            sumTrialFitness = 0
            testedGenome = genomes[b]
            #print(f"Trial for genome: {testedGenome}")


            # doing the thing c times (freeballing for a bit here)
            for c in range(trials):
                world = genRandomWorld(length)
                #print(f"starging world: {world}")
                Count1 = np.count_nonzero(world)
                if (length-Count1)>=length//2:
                    want = 1
                else: want = 0
                for d in range(trialLength):
                    position = 0
                    nextStep = np.array([0]*length)
                    for e in range(length):
                        # checkDO
                        rule = checkDo(viewSize,testedGenome, world, position, length, stupidArray)
                        # end checkDo
                        nextStep[e] = rule
                        position = position + 1
                        # we have now done one step of the trial
                        # now we set the new world to be the world var and do it agian
                        
                    world = nextStep
                # after the trial, we need this trial's fitness
                # fitness is 5 if the difusion grew, or 0 if it shrank
                ones = np.count_nonzero(world)
                zeroes = length - ones
                if want == 1 and ones>Count1:
                    fitness = 7
                elif want == 0 and ones<Count1:
                    fitness = 7
                else:
                    fitness = -2
                sumTrialFitness = sumTrialFitness + fitness
            #after all the trials are done, the fitness is averaged and added to fitList
            avgFit = sumTrialFitness / trials
            fitList[b] = avgFit
        #print(f"fitList is {fitList}")
        # ok now we have the list of fitnesses for each genome in the population
        # gen next gen typa beat
        sortsIND = fitList.argsort()
        sortedGenomes = genomes[sortsIND[::-1]]
        sortedFitness = fitList[sortsIND[::-1]]
        for x in range(populationSize//2):
            p1 = random.choices(sortedGenomes, dummyArray)[0]
            p2 = random.choices(sortedGenomes, dummyArray)[0]
            c1, c2 = crossover(p1,p2,crossover_)
            c1 = mutate(c1, mutation_)
            c2 = mutate(c2, mutation_)
            newGen[2*x] = c1
            newGen[2*x+1] = c2
        genomes = newGen
        genomeStorage[a] = sortedGenomes[0]
        fitnessStorage[a] = sortedFitness[0]
        #print(f"1 generation completed\nNew Generation:\n{genomes}")
    print(f"all done :D\n best fitnesses are:\n{fitnessStorage}\n with genomes:\n{genomeStorage}")


@jit(nopython=True)
def checkDo(viewSize,testedGenome, world, position, length, stupidArray):
    away = (viewSize-1)//2
    sight = np.array([0]*viewSize)
    for f in range(away):
        sight[f] = world[position-(away-f)]
    sight[away] = world[position]
    for f in range(1,away+1):
        sight[away+f] = world[(position+f)%length]
    string = ''
    for f in sight:
        if f == 1:
            string += '1'
        if f == 0:
            string += '0'
    indexs = np.where(stupidArray == string,1,0)
    index = 0
    for x in range(2**viewSize):
        if x == 0:
            index +=1
        if x == 1:
            break
    rule = testedGenome[index]
    return rule

def genRandomWorld(length):
    world = np.array([0]*length)
    for x in range(length):
        world[x] = random.randrange(0,2)
    return world

@jit(nopython=True)
def genRanGenome(length):
    genome = ''
    for x in range(length):
        genome += str(random.randrange(0,2))
        gen = strToInt(genome)
    return genome

@jit(nopython=True)
def strToInt(string):
    total = 0
    multiplier = 1
    for x in range(len(string)):
        idd = string[len(string)-x-1]
        if idd == '0':
            pass
        if idd == '1':
            total = total + multiplier
        multiplier = multiplier*2
    return total

@jit(nopython=True)        
def intToStr(number):
    remainders = ''
    while number != 0:
        rem = number%2
        if rem == 1:
            remainders = '1'+remainders
        if rem == 0:
            remainders = '0'+remainders
        number = number//2
    return remainders

@jit(nopython=True)
def mutate(genome, mutation_):
    newG = ''
    for x in range(len(genome)):
        if random.uniform(0,1) < mutation_:
            newG += swapChamp(genome[x])
        else: newG += genome[x]
    return newG

@jit(nopython=True)
def crossover(p1, p2, crossover_):
    if random.uniform(0,1) < crossover_:
        cPoint = random.randrange(1,len(p1))
        p1l = p1[:cPoint]
        p1r = p1[cPoint:]
        p2l = p2[:cPoint]
        p2r = p2[cPoint:]
        c1 = p1l + p2r
        c2 = p2l + p1r
        return c1,c2
    else: return p1,p2


@jit(nopython=True)
def swapChamp(bit):
    if bit == '1': return '0'
    if bit == '0': return '1'
