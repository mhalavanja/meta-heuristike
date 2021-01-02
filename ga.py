import numpy as np
import hc
import ga
import helper

# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
# Stochastic universal sampling
def SUSSelection(generation: np.array, line: np.array, fitSum: int, n: int, k: int):
    selected = []
    p = fitSum/float(k)
    [r] = np.random.uniform(0, p, 1)
    j = 0
    curPointer = r
    while curPointer < line[0][0]:
            j += 1
            curPointer = r + float(j * p)
    for i in range(n):    
        while curPointer > line[i][0] and curPointer < line[i][1]:
            selected.append(generation[i])
            j += 1
            curPointer = r + float(j * p)
    assert len(selected) == k
    return selected

def topSelection(generation: np.array, fitnes: np.array, n: int, k: int):
    inds = np.array(fitnes).argsort()[::-1] 
    generation = np.array(generation, tuple)[inds]
    return generation[:k]
    
def mutateGeneration(n: int, generation: np.array):
    def mutate(n: int, sol: tuple):
        order, enc = sol
        # swapPairs = np.random.randint(0, n, 2)
        # [changeWhat] = np.random.randint(0, 2, 1)
        encToChange = np.random.randint(0, len(enc), 2)
        while encToChange[0] == encToChange[1]:
            encToChange = np.random.randint(0, len(enc), 2)
        # if changeWhat == 0 or encToChange[0] == encToChange[1]:
        
        #     return(helper.swap(order, swapPairs[0], swapPairs[1]), enc)
        # else:
        #     return(order, helper.changeEnc(enc, encToChange[0], encToChange[1]))
        if encToChange[0] != encToChange[1]:
            return(order, helper.changeEnc(enc, encToChange[0], encToChange[1]))
    mutation = np.random.choice(2, n, p=[0.80, 0.20]) #mogucnost mutacije
    for i in range(n):
        if mutation[i] == 1:
            generation[i] = mutate(n, generation[i])
    return generation

# 1) Koristimo križanje poretka zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossingForGA(n: int, k: int, population: np.array):
    def crossing(n: int, solA: tuple, solB: tuple):
        [pos1, pos2] = np.random.randint(0, n, 2)
        if pos2 < pos1:
            tmp = pos1
            pos1 = pos2
            pos2 = tmp
        [orderA, encA] = solA
        [orderB, encB] = solB
        childAord = np.full(n, np.nan, int)
        childBord = np.full(n, np.nan, int)
        setA = set()
        setB = set()
        #sljedeci dio koda je realizacija križanja, križa se samo order bez enc za sad
        for i in range(pos1, pos2):
            childAord[i] = orderA[i]
            setA.add(orderA[i])
            childBord[i] = orderB[i]
            setB.add(orderB[i])
        j = pos2
        for i in range(pos2, n):
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                setA.add(orderB[i])
                j += 1
        for i in range(0, pos2):
            if j == n:
                j = 0
            elif j == pos1:
                break
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                setA.add(orderB[i])
                j += 1
        j = pos2
        for i in range(pos2, n):
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                setB.add(orderA[i])
                j += 1
        for i in range(0, pos2):
            if j == n:
                j = 0
            elif j == pos1:
                break
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                setB.add(orderA[i])
                j += 1
        return ((childAord, encA), (childBord, encB))

    # [l, s] = np.random.randint(0, n, 2) # l -> duljina ntupa, s -> startni indeks
    mutation = np.random.choice(2, n, p=[0.95, 0.05]) #mogucnost mutacije
    newGeneration = []
    cur = 0
    while cur < n:
        indices = np.random.randint(0, k, k)
        for i in range(k):
            a = population[i] #jos [0] ako se i fit prenosi s populacijom
            # t = (2 * i + n//3) % k
            b = population[indices[i]]
            # print(type(a[0]), type(a[0]))
            # count = 0
            # while not np.any(a[0] - b[0]):
            #     try:
            #         assert count < 100
            #     except AssertionError:
            #         break
            #     [t] = np.random.randint(0, k, 1)
            #     b = population[t]
            #     count += 1
            c, d = crossing(n, a, b)
            if cur == n:
                assert None not in newGeneration
                return newGeneration
            cur += 1
            newGeneration.append(c)
            cur += 1
            newGeneration.append(d)
            if cur == n:
                assert None not in newGeneration
                return newGeneration

# 1) k je veličina populacije za križanje
def geneticAlgorithm(n: int, k: int, numOfIter: int, matrix: np.array):
    generation = []
    newGeneration = []
    fitSum = 0
    line = []
    bestFit = 0
    bestSol = None
    fitnes = []
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
                fitnes.append(fit)
            # selected = SUSSelection(generation, line, fitSum, n, k)
            selected = topSelection(generation, fitnes, n, k)
            generation = crossingForGA(n, k, selected)
            generation = mutateGeneration(n, generation)
        else:
            fitSum = 0
            line = []
            fitnes = []
            newGeneration = []
            for i in range(n):
                assert len(generation) == n
                sol = generation[i]
                fit = helper.getFitnessOfSolution(sol, matrix)
                if fit > bestFit:
                    bestFit = fit
                    bestSol = sol
                newFitSum = fitSum + fit
                line.append((fitSum, newFitSum))
                fitSum = newFitSum
                newGeneration.append(sol)
                fitnes.append(fit)
            generation = newGeneration
            # selected = SUSSelection(generation, line, fitSum, n, k)
            selected = topSelection(generation, fitnes, n, k)
            generation = crossingForGA(n, k, selected)
            generation = mutateGeneration(n, generation)
    return (bestSol, bestFit)
