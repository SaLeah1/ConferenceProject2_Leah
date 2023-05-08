import random
from graphics import *
import time
import matplotlib.pyplot as plt

Random = 37
aLen = 40
viewSize = 7 #Viewsize must be odd
randGenome = [random.randrange(0,2) for x in range (2**viewSize)]

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

class Strip:
    length = aLen
    array = []
    position = 0
    objects = []
    genome ='0'*(2**viewSize)
    window = None
    
    def __init__(self, Array = [0]*length):
        self.array = Array
        self.length = len(self.array)
        self.position = 0
        
    def setWindow(self):
        self.window = GraphWin("1DCA", 1240,200)
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
        away = (viewSize-1)//2
        sight = []
        for x in range(away):
            sight.append(self.array[self.position-(away-x)])
        sight.append(self.array[self.position])
        for x in range(1,away+1):
            sight.append(self.array[(self.position+x)%self.length])
        string = ''
        for x in sight:
            string += str(x)
        index = stupidArray.index(string)
        toDo = self.genome[index]
        return toDo

    def randomize(self,quiet=True):
        for x in range(self.length):
            self.array[x] = random.randrange(0,2)
        if not quiet:
            self.draw()

    def step(self):
        newGen = []
        self.position = 0
        for x in range(self.length):
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
        sqs = 1200//self.length
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
                time.sleep(0.25)
        return self.array

def weighted_choice(elements, weights):
    offset = min(weights)
    positiveweights = [z - offset + 1 for z in weights]
    choices = random.choices(elements, positiveweights)
    for x in range(100):
      if weights[elements.index(choices[0])]<0:
        choices = random.choices(elements, positiveweights)
      else:
        break      
    return choices[0]


class GAController:

    world = Strip()
    popSize = 14
    population = []
    genomeSize = 2**viewSize
    mutation_ = 0.05
    crossover_ = 1
    dummyList = [x+1 for x in range(popSize)]
    trialLen = 400
    numTrials = 15
    
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
            fav = 0
            genome = self.population[x]
            for z in range(self.numTrials):
                  self.world.setGenome(genome)
                  worldArray = [random.choice([0,1]) for q in range(aLen)]
                  self.world.set(worldArray)
                  want, count = self.detWant(worldArray)
                  theArray = self.world.runFor(self.trialLen,True)
                  num1s = self.world.array.count(1)
                  num0s = self.world.array.count(0)
                  if want == 1 and num1s>count:
                      fitness = 7
                  if want == 0 and num0s>count:
                      fitness = 7
                  else:
                      fitness = -7
                  fav += fitness
            fav = fav/self.numTrials
            fitList[x]=fav
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
            print(f"starting run {x} of {runs}")
            fitness, genome = self.genNext()
            genomes[x] = genome
            fitnesses[x] = fitness
        index = fitnesses.index(max(fitnesses))
        fMax = fitnesses[index]
        gMax = genomes[index]
        print(f"Best Fitness was {fMax} in generation {index}\nGenome: {gMax}")
        fig = plt.figure()
        sam = fig.add_subplot(111)
        sam.plot(fitnesses)
        fig.show()
        #plt.plot(sArray,fitnesses)

    def testGenome(self,genome,tests):
        array = [0]*128
        for x in range(len(genome)):
            array[x] = int(genome[x])
        self.world.setGenome(array)
        corrects = 0
        failed1s = 0
        failed0s = 0
        total1s = 0
        total0s = 0
        for x in range(tests):
            print(f"staring test {x} of {tests}")
            self.world.randomize()
            want = self.detWant(self.world.array)[0]
            starting1s = self.world.array.count(1)
            starting0s = self.world.array.count(0)
            self.world.runFor(self.trialLen, True)
            end1s = self.world.array.count(1)
            end0s = self.world.array.count(0)
            if want == 1 and end1s>=starting1s:
                print(f"Want = {want}\nPASSED")
                corrects +=1
                total1s +=1
            if want == 0 and end0s>=starting0s:
                print(f"Want = {want}\nPASSED")
                corrects +=1
                total0s +=1
            if want == 0 and end0s<starting0s:
                print(f"Want = {want}\nFAILED")
                failed0s += 1
                total0s +=1
            if want == 1 and end1s<starting1s:
                print(f"Want = {want}\nFAILED")
                failed1s += 1
                total1s +=1
            print()
        print()
        print(f"Genome had a {(corrects/tests)*100:.2f}% sucsess rate")
        print(f"Genome failed {failed1s} / {total1s} 1s and {failed0s} / {total0s} 0s")

    def detWant(self,Array):
        count1 = Array.count(1)
        count0 = len(Array) - count1
        if count1 >= count0:
            return 1,count1
        else: return 0,count0
