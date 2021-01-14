import numpy as np
import hc
import ga
import helper

# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
# Stochastic universal sampling
def SUSSelection(generation: np.array, line: np.array, fitSum: int, n: int, k: int):
    selected = np.empty(k, dtype=object)
    p = fitSum/float(k)
    [r] = np.random.uniform(0, p, 1)
    j = 0
    curPointer = r
    cur = 0
    while curPointer < line[0][0]:
            j += 1
            curPointer = r + float(j * p)
    for i in range(n):    
        while curPointer > line[i][0] and curPointer < line[i][1]:
            selected[cur] = generation[i]
            cur += 1
            j += 1
            curPointer = r + float(j * p)
    assert None not in selected
    return selected

def topSelection(generation: np.array, fitnes: np.array, n: int, k: int):
    inds = np.array(fitnes).argsort()[::-1] 
    generation = np.array(generation, tuple)[inds]
    return generation[:k]
    
def mutateGeneration(n: int, generation: np.array, rng):
    def mutate(n: int, sol: tuple, rng):
        order, enc = sol
        newOrder = order.copy()
        newEnc = enc.copy()
        # swapPairs = np.random.randint(0, n, 2)
        # [changeWhat] = np.random.randint(0, 2, 1)
        encToChange = rng.choice(len(enc), 2, replace=False)
        # if changeWhat == 0 or encToChange[0] == encToChange[1]:
        
        #     return(helper.swap(newOrder, swapPairs[0], swapPairs[1]), enc)
        # else:
        #     return(order, helper.changeEnc(newEnc, encToChange[0], encToChange[1]))
        return(order, helper.changeEnc(newEnc, encToChange[0], encToChange[1]))

    mutation = np.random.choice(2, n, p=[0.950, 0.050]) #mogucnost mutacije
    for i in range(n):
        if mutation[i] == 1:
            generation[i] = mutate(n, generation[i], rng)
    return generation

# 1) Koristimo križanje poretka zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossingForGA(n: int, k: int, selected: np.array, rng):
    def crossing(n: int, solA: tuple, solB: tuple):
        [pos1, pos2] = np.random.randint(0, n, 2)
        if pos2 < pos1:
            tmp = pos1
            pos1 = pos2
            pos2 = tmp

        [realOrderA, realEncA] = solA
        [realOrderB, realEncB] = solB
        orderA = realOrderA.copy()
        orderB = realOrderB.copy()
        encA = realEncA.copy()
        encB = realEncB.copy()

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
    newGeneration = []
    cur = 0
    while cur < n:
        indices = rng.choice(k, n//2 + 1, replace=True)
        for i in range(k):
            a = selected[indices[i]] #jos [0] ako se i fit prenosi s populacijom
            # t = (2 * i + n//3) % k
            b = selected[indices[i + 1]]
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
            cur += 1
            newGeneration.append(c)
            if cur == n:
                return newGeneration
            cur += 1
            newGeneration.append(d)
            if cur == n:
                return newGeneration
    return newGeneration

# 1) k je veličina populacije za križanje
def geneticAlgorithm(n: int, k: int, numOfIter: int, matrix: np.array):
    generation = np.array([helper.getRandomStartingSolution(n) for _ in range(n)], dtype=object)
    line = np.empty(n, dtype=object)
    fitnes = np.empty(n, dtype=int)
    rng = np.random.default_rng()
    bestFit = 0
    bestSol = None

    for __ in range(numOfIter):    
        assert len(generation) == n
        fitSum = 0

        for i in range(n):
            sol = generation[i]
            fit = helper.getFitnessOfSolution(sol, matrix)
            if fit > bestFit:
                bestFit = fit
                bestSol = sol
            newFitSum = fitSum + fit
            line[i] = (fitSum, newFitSum)
            fitSum = newFitSum
            generation[i] = sol
            fitnes[i] = fit

        # selected = SUSSelection(generation, line, fitSum, n, k)
        selected = topSelection(generation, fitnes, n, k)
        generation = crossingForGA(n, k, selected, rng)
        generation = mutateGeneration(n, generation, rng)        
    for i in range(n):
        assert len(generation) == n
        sol = generation[i]
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            bestSol = sol
    return (bestSol, bestFit)
