import random
from graphics import *
import time
import matplotlib.pyplot as plt

Random = 37
aLen = 200
Glorp = [1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0]
Glorp2 = [1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0,1,1,0,0]
gRandom = [random.choice([0,1]) for x in range(aLen)]
gTest = [1]*aLen

def genStupidArray(n):
    if n == 1:
        return ['0', '1',]
    else:
        shorter_strings = genStupidArray(n-1)
        with_0 = ['0'+b for b in shorter_strings]
        with_1 = ['1'+b for b in shorter_strings]
        all = with_0 + with_1
        return all

stupidArray = genStupidArray(3)

class Strip:
    length = aLen
    array = []
    position = 0
    objects = []
    genome ='0'*8
    window = None
    
    def __init__(self, Array = [0]*length):
        self.array = Array
        self.length = len(self.array)
        self.position = 0
        
    def setWindow(self):
        self.window = GraphWin("1DCA", 820,100)
        self.draw()

    def __str__(self):
        string = ""
        for x in self.array:
            if x == 0:
                string += "⬜"
            if x == 1:
                string += "⬛"
        return string
    
    def checkDo(self):
        right = self.array[(self.position+1)%self.length]
        core = self.array[self.position]
        left = self.array[self.position-1]
        index = stupidArray.index(f"{left}{core}{right}")
        #print(index)
        #print(f"{left}{core}{right}")
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
            #print(self.position, len(newGen), len(self.array))
            bit = self.checkDo()
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
        sqs = 800//self.length
        buf = 10
        #print(f"{leng}   {xSpace}    {buf}")
        for x in range(self.length):
            if self.array[x] == 1:
                sq = Rectangle(Point(x*sqs+buf,50-(sqs//2)),Point((x+1)*sqs+buf,50+(sqs//2)))
                sq.setFill("black")
                sq.setOutline("blue")
                self.objects.append(sq)
                sq.draw(self.window)
            if self.array[x] == 0:
                sq = Rectangle(Point(x*sqs+buf,50-(sqs//2)),Point((x+1)*sqs+buf,50+(sqs//2)))
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

    world = Strip()
    popSize = 10
    population = []
    genomeSize = 8
    mutation_ = 0.05
    crossover_ = 1
    dummyList = [x+1 for x in range(popSize)]
    targetStrip = []
    
    def __init__(self, targetStrip = [1]*aLen):
        self.target = targetStrip
        aLen = len(targetStrip)
        for x in range(self.popSize):
            genome = []
            for x in range(self.genomeSize):
                genome.append(random.choice([0,1]))
            self.population.append(genome)
        #print(self.population)
        #self.world.setWindow()
        targetString = ""
        for x in self.target:
            if x == 0:
                targetString += "⬜"
            if x == 1:
                targetString += "⬛"
        print(f"Target:\n{targetString}")

    def genFitness(self):
        fitList = []
        #print(self.population)
        for x in self.population:
            fav = []
            for z in range(3):
                  self.world.setGenome(x)
                  self.world.set([random.choice([0,1]) for q in range(aLen)])
                  theArray = self.world.runFor(100,True)
                  fitness = 0
                  for w in range(len(theArray)):
                        if theArray[w] == self.target[w]:
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
        tenper = runs//10
        perten = 1
        for x in range(runs):
            fitness, genome = self.genNext()
            genomes.append(genome)
            fitnesses.append(fitness)
            if x%tenper == 0:
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
        
