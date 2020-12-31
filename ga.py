import numpy as np
import hc
import ga
import helper


#TODO: implementirati GA sljedece
# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
def selectionForGA(generation: np.array, line: np.array, fitSum: int, k: int):
    selected = []
    p = fitSum/float(k)
    [r] = np.random.uniform(0, p, 1)
    cur = 0
    for i in range (k):
        curPointer = r + float(i * p)
        while curPointer - line[cur][0] < 0:
            cur += 1
        selected.append(generation[cur])
    return selected

def mutate(n: int, sol: tuple):
    order, enc = sol
    swapPairs = np.random.randint(0, n, 2)
    [changeWhat] = np.random.randint(0, 2, 1)
    encToChange = np.random.randint(0, len(enc), 2)
    if changeWhat == 0 or encToChange[0] == encToChange[1]:
        return(helper.swap(order, swapPairs[0], swapPairs[1]), enc)
    else:
        return(order, helper.changeEnc(enc, encToChange[0], encToChange[1]))

# 1) Koristimo križanje poretka zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossingForGA(n: int, k: int, population: np.array):
    def crossing(n: int, solA: tuple, solB: tuple):
        # [pos1, pos2] = np.random.randint(0, n, 2)
        [pos1] = np.random.randint(0, n/2, 1)
        pos2 = pos1 + int(n / 2)
        if pos2 < pos1:
            tmp = pos1
            pos1 = pos2
            pos2 = tmp
        [orderA, encA] = solA
        [orderB, encB] = solB
        childAord = [None] * n 
        childBord = [None] * n
        setA = set()
        setB = set()
        for i in range(pos1, pos2):
            childAord[i] = orderA[i]
            setA.add(orderA[i])
            childBord[i] = orderB[i]
            setB.add(orderB[i])
        j = pos2
        for i in range(pos2, n):
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                j += 1
        for i in range(0, pos1):
            if j == n:
                j = 0
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                j += 1
        j = pos2
        for i in range(pos2, n):
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                j += 1
        for i in range(0, pos1):
            if j == n:
                j = 0
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                j += 1
        return ((childAord, encA), (childBord, encB))

    # [l, s] = np.random.randint(0, n, 2) # l -> duljina ntupa, s -> startni indeks
    mutation = np.random.choice(2, n, p=[0.95, 0.05])
    newGeneration = []
    # l = l % 3 + 1
    cur = 0
    while cur < n:
        for i in range(k):
            a = population[i] #jos [0] ako se i fit prenosi s populacijom
            b = population[(2 * i) % k]
            c, d = crossing(n, a, b)
            if mutation[cur] == 1:
                c = mutate(n, c)
            if cur == n:
                return newGeneration
            cur += 1
            newGeneration.append(c)
            if mutation[cur] == 1:
                d = mutate(n, d)
            cur += 1
            newGeneration.append(d)
            if cur == n:
                return newGeneration
    return newGeneration

# 1) k je veličina populacije za križanje
def geneticAlgorithm(n: int, k: int, numOfIter: int, matrix: np.array):
    generation = []
    fitSum = 0
    line = []
    bestFit = 0
    bestSol = None
    for __ in range(numOfIter):    
        if len(generation) == 0:
            for __ in range(n):
                sol = helper.getRandomStartingSolution(n)
                fit = helper.getFitnessOfSolution(sol, matrix)
                if fit > bestFit:
                    bestFit = fit
                    bestSol = sol
                newFitSum = fitSum + fit
                line.append((fitSum, newFitSum))
                fitSum = newFitSum
                generation.append(sol) #mozda mozemo ovaj fit iskoristit i za kasnije
            selected = selectionForGA(generation, line, fitSum, k)
            generation = crossingForGA(n, k, selected)
        else:
            for i in range(n):
                sol = generation[i]
                fit = helper.getFitnessOfSolution(sol, matrix)
                if fit > bestFit:
                    bestFit = fit
                    bestSol = sol
                newFitSum = fitSum + fit
                fitSum = newFitSum
                line.append((fitSum, newFitSum))
                generation.append((sol, fit))
            selected = selectionForGA(generation, line, fitSum, k)
            generation = crossingForGA(n, k, selected)
    return (bestSol, bestFit)
