import random
from graphics import *
import time
import matplotlib.pyplot as plt

Random = 37
aLen = 40
Glest = [1]*aLen

randGenome = [random.randrange(0,2) for x in range(512)]
randStrip = []
for x in range(aLen):
    line = [random.randrange(0,2) for x in range(aLen)]
    randStrip.append(line)



def genStupidArray(n):
      if n == 1:
        return ['0', '1',]
      else:
        shorter_strings = genStupidArray(n-1)
        with_0 = ['0'+b for b in shorter_strings]
        with_1 = ['1'+b for b in shorter_strings]
        all = with_0 + with_1
        return all

stupidArray = genStupidArray(9)

class Strip:
    length = aLen
    array = [[]]
    posX = 0
    posY = 0
    objects = []
    genome ='0'*(2**9)
    window = None
    
    def __init__(self, Array = [[0]*length]*length, Genome = '0'*512):
        self.array = Array
        self.length = len(self.array)
        self.posX = 0
        self.posY = 0
        
    def setWindow(self):
        self.window = GraphWin("1DCA", 820,100)
        self.draw()

    def __str__(self):
        string = ''
        for y in range(self.length):
            for x in range(self.length):
                bit = self.array[y][x]
                if bit == 0 or bit == '0':
                    string += "⬜"
                if bit == 1 or bit == '1':
                    string += "⬛"
            string += '\n'
        return string[:-1]
    
    def checkDo(self):
        uLeft = self.array[self.posY-1][self.posX-1]
        uMid = self.array[self.posY-1][self.posX]
        uRight = self.array[self.posY-1][(self.posX+1)%self.length]
        cLeft = self.array[self.posY][self.posX-1]
        Core = self.array[self.posY][self.posX]
        cRight = self.array[self.posY][(self.posX+1)%self.length]
        dLeft = self.array[(self.posY+1)%self.length][self.posX-1]
        dMid = self.array[(self.posY+1)%self.length][self.posX]
        dRight = self.array[(self.posY+1)%self.length][(self.posX+1)%self.length]
        index = stupidArray.index(f"{uLeft}{uMid}{uRight}{cLeft}{Core}{cRight}{dLeft}{dMid}{dRight}")
        toDo = self.genome[index]
        return toDo

    def randomize(self,quiet = True):
        newArray = []
        for y in range(self.length):
            newArray.append([random.randrange(0,2)])
            for x in range(self.length-1):
                randy = random.randrange(0,2)
                newArray[y].append(randy)
        self.array = newArray
        if quiet != True:
            print(self)

    def step(self):
        newGen = []
        self.posY = 0
        for y in range(self.length):
            newGen.append([self.checkDo()])
            self.posX = 0
            for x in range(self.length-1):
                bit = self.checkDo()
                newGen[y].append(bit)
                self.posX += 1
            self.posY += 1
        if len(newGen) != len(self.array):
            print("oh no")
        self.array = newGen

    def setGenome(self,genome):
        self.genome = genome

    def set(self,array):
        self.array = array

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


class GAController:

    world = None
    popSize = 10
    population = []
    boardSize = aLen
    genomeSize = 512 ## THIS CAN NOT BE CHANGED
    mutation_ = 0.05
    crossover_ = 1
    dummyList = [x+1 for x in range(popSize)]
    targetStrip = []
    
    def __init__(self, targetStrip = [[1]*boardSize]*boardSize):
        self.world = Strip()
        self.targetStrip = targetStrip
        for x in range(self.popSize):
            genome = []
            for x in range(self.genomeSize):
                genome.append(random.choice([0,1]))
            self.population.append(genome)
        #print(self.population)
        #self.world.setWindow()
        print(f"Created GA Controller\nMutation Rate: {self.mutation_} Crossover Rate: {self.crossover_}")
        print("Target:")
        print(self.printOut(self.targetStrip))

    def genFitness(self):
        fitList = []
        for x in self.population:
            fav = []
            for z in range(3):
                  self.world.setGenome(x)
                  self.world.randomize()
                  theArray = self.world.runFor(100,True)
                  fitness = 0
                  for w in range(self.boardSize):
                      for v in range(self.boardSize):
                          if theArray[w][v] == self.targetStrip[w][v]:
                              fitness +=1
                  fav.append(fitness)
            aFav = sum(fav)//len(fav)
            fitList.append(aFav)
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
        newG = []
        for x in range(len(genome)):
            if random.uniform(0,1) < self.mutation_:
                newG.append(self.swapChamp(genome[x]))
            else: newG.append(genome[x])
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
        genomes = []
        fitnesses = []
        tenper = runs//100
        perten = 0
        for x in range(runs):
            fitness, genome = self.genNext()
            genomes.append(genome)
            fitnesses.append(fitness)
            perten += 1
            if perten%tenper == 0:
                  print(f"{perten//tenper}% completed")
        index = fitnesses.index(max(fitnesses))
        fMax = fitnesses[index]
        gMax = genomes[index]
        print(f"Best Fitness was {fMax} in generation {index}\nGenome: {gMax}")
        fig = plt.figure()
        sam = fig.add_subplot(111)
        sam.plot(fitnesses)
        fig.show()
        
    def printOut(self,board):
        string = ''
        for y in range(self.boardSize):
            for x in range(self.boardSize):
                bit = self.targetStrip[y][x]
                if bit == 0 or bit == '0':
                    string += "⬜"
                if bit == 1 or bit == '1':
                    string += "⬛"
            string += '\n'
        return string[:-1]
        
