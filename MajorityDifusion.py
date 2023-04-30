import random
from graphics import *
import time
import matplotlib.pyplot as plt
import numpy as np
from numba import jit
from numba import int32,float32
from numba.experimental import jitclass

Random = 37
aLen = 100
viewSize = 3 #Viewsize must be odd
randGenome = [random.randrange(0,2) for x in range (2**viewSize)]

spec = [
    ('value', int32),               # a simple scalar field
    ('array', float32[:]),
    ]

def genStupidArray(n):
    if n == 1:
        return ['0', '1',]
    else:
        shorter_strings = genStupidArray(n-1)
        with_0 = ['0'+b for b in shorter_strings]
        with_1 = ['1'+b for b in shorter_strings]
        all = with_0 + with_1
        return all

stupidArray = genStupidArray(viewSize)

@jitclass(spec)
class Strip:
    
    def __init__(self, array = [0]*aLen):
        self.array = array
        self.length = aLen
        self.position = 0
        self.objects = []
        self.genome = '0'*(2**viewSize)
        window = None
        
    def setWindow(self):
        self.window = GraphWin("1DCA", 1640,200)
        self.draw()

    def __str__(self):
        string = ""
        for x in self.array:
            if x == 0:
                string += "⬜"
            if x == 1:
                string += "⬛"
        return string

    def checkDo(self,viewsize):
        away = (viewsize-1)//2
        sight = [0]*viewsize
        for x in range(away):
            sight[x]=self.array[self.position-(away-x)]
        sight[away]=self.array[self.position]
        for x in range(1,away+1):
            sight[away+x-1]=self.array[(self.position+x)%self.length]
        string = ''
        for x in sight:
            string += str(x)
        index = stupidArray.index(string)
        toDo = self.genome[index]
        return toDo

    def randomize(self):
        for x in range(self.length):
            self.array[x] = random.randrange(0,2)
        self.draw()

    def step(self):
        newGen = []
        self.position = 0
        for x in range(self.length):
            bit = self.checkDo(viewSize)
            newGen.append(bit)
            self.position += 1
        if len(newGen) != len(self.array):
            print("oh no")
        self.array = newGen

    def setGenome(self,genome):
        self.genome = genome

    def set(self,array):
        self.array = array
        
    def draw(self):
        for z in self.objects:
            z.undraw()
        self.objects = []
        sqs = 1600//self.length
        buf = 20
        for x in range(self.length):
            ecks = self.array[x]
            if ecks == 1 or ecks == '1':
                sq = Rectangle(Point(x*sqs+buf,100-(sqs//2)),Point((x+1)*sqs+buf,100+(sqs//2)))
                sq.setFill("black")
                sq.setOutline("blue")
                self.objects.append(sq)
                sq.draw(self.window)
            if ecks == 0 or ecks == '0':
                sq = Rectangle(Point(x*sqs+buf,100-(sqs//2)),Point((x+1)*sqs+buf,100+(sqs//2)))
                sq.setOutline("blue")
                self.objects.append(sq)
                sq.draw(self.window)

    def filled(self):
        return self.array.count(1)

    def runFor(self, generations = 10, quiet = False):
        for x in range(generations):
            self.step()
            if quiet == False:
                self.draw()
                #print(f"{x:3}: {self}")
                time.sleep(0.05)
        return self.array

@jit(nopython=True)
def weighted_choice(elements, weights):
    total = sum(weights)
    choiche = random.uniform(0,total)
    w = 0
    for x in range(len(elements)):
        w = w + weights[x]
        if w>choiche:
            return elements[x]
        else:
            pass
    return random.choice(elements)

@jitclass(spec)
class GAController:

    world = Strip()
    popSize = 10
    population = []
    genomeSize = 2**viewSize
    mutation_ = 0.05
    crossover_ = 1
    dummyList = [x+1 for x in range(popSize)]
    
    def __init__(self):
        for x in range(self.popSize):
            genome = []
            for x in range(self.genomeSize):
                genome.append(random.choice([0,1]))
            self.population.append(genome)
        #print(self.population)
        #self.world.setWindow()
        print("Created Majority Difusion GAController")
                
    def genFitness(self):
        fitList = [None]*self.popSize
        #print(self.population)
        for x in range(self.popSize):
            fav = [0]*10
            genome = self.population[x]
            for z in range(10):
                  self.world.setGenome(genome)
                  worldArray = [random.choice([0,1]) for q in range(aLen)]
                  self.world.set(worldArray)
                  want = self.detWant(worldArray)
                  theArray = self.world.runFor(100,True)
                  fitness = 0
                  for w in range(len(theArray)):
                        if theArray[w] == want:
                              fitness +=1
                  fav[z]=fitness
            aFav = sum(fav)//len(fav)
            fitList[x]=aFav
        return fitList

    def crossover(self, p1, p2):
        if random.uniform(0,1) < self.crossover_:
            cPoint = random.randrange(1,len(p1))
            p1l = p1[:cPoint]
            p1r = p1[cPoint:]
            p2l = p2[:cPoint]
            p2r = p2[cPoint:]
            c1 = p1l+p2r
            c2 = p2l +p1r
            assert len(c1) == len(c2) == self.genomeSize, "uh-oh"
            return c1,c2
        else: return p1,p2

    def mutate(self, genome):
        newG = [0]*len(genome)
        for x in range(len(genome)):
            if random.uniform(0,1) < self.mutation_:
                newG[x]=self.swapChamp(genome[x])
            else: newG[x]=genome[x]
        return newG

    def swapChamp(self,bit):
        if bit == 1: return 0
        if bit == 0: return 1
        
    def genNext(self):
        newGen = []
        fitList = self.genFitness()
        #print(fitList)
        sorts = [x for _,x in sorted(zip(fitList,self.population))]
        for x in range(len(self.population)//2):
            p1 = weighted_choice(sorts, self.dummyList)
            p2 = weighted_choice(sorts, self.dummyList)
            c1,c2 = self.crossover(p1,p2)
            c1 = self.mutate(c1)
            c2 = self.mutate(c2)
            newGen.append(c1)
            newGen.append(c2)
        #print(newGen)
        self.population = newGen
        #print(f"best Fitness: {max(fitList)}\nGenome: {sorts[1]}")
        return max(fitList),sorts[1]

    def runFor(self,runs):
        # these are autosorted
        sArray = [x for x in range(runs)]
        genomes = [0]*runs
        fitnesses = [0]*runs
        tenper = runs//10
        perten = 0
        for x in range(runs):
            fitness, genome = self.genNext()
            genomes[x] = genome
            fitnesses[x] = fitness
            if tenper == 0 or x%tenper == 0:
                  print(f"{perten*10}% completed")
                  perten += 1
        index = fitnesses.index(max(fitnesses))
        fMax = fitnesses[index]
        gMax = genomes[index]
        print(f"Best Fitness was {fMax} in generation {index}\nGenome: {gMax}")
        fig = plt.figure()
        sam = fig.add_subplot(111)
        sam.plot(fitnesses)
        fig.show()
        #plt.plot(sArray,fitnesses)

    def detWant(self,Array):
        count1 = Array.count(1)
        count0 = len(Array) - count1
        if count1 >= count0:
            return 1
        else: return 0
        
