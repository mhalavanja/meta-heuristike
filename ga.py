import numpy as np
import hc
import ga
import helper

# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
# Stochastic universal sampling
def SUSSelection(generation, line, fitSum: int, n: int, k: int):
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

def topSelection(generation, fitnes, n: int, k: int):
    inds = np.array(fitnes).argsort()[::-1] 
    generation = np.array(generation, tuple)[inds]
    return generation[:k]

# 1) TODO: Mogli bi imati dvije mutacije, jedna mtuacija za order, druga za enc 
def mutateGeneration(n: int, generation, rng):
    def mutateEnc(sol: tuple, rng):
        order, enc = sol
        newOrder = order.copy()
        newEnc = enc.copy()
        encToChange = rng.choice(len(enc), 2, replace=False)
        return(newOrder, helper.changeEnc(newEnc, encToChange[0], encToChange[1]))

    def mutateOrder(n: int, sol: tuple, rng):
        order, enc = sol
        newOrder = order.copy()
        newEnc = enc.copy()
        orderToChange = rng.choice(n, 2, replace=False)
        return(helper.swap(newOrder, orderToChange[0], orderToChange[1]), newEnc)

    mutationEnc = np.random.choice(2, n, p=[0.90, 0.10]) #mogucnost mutacije enclousera
    mutationOrder = np.random.choice(2, n, p=[0.99, 0.01]) #mogucnost mutacije ordera
    
    for i in range(n):
        if mutationEnc[i] == 1:
            generation[i] = mutateEnc(generation[i], rng)
        if mutationOrder[i] == 1:
            generation[i] = mutateEnc(generation[i], rng)
    return generation

# 1) Koristimo križanje poretka (OX1) zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossoverOfSelectedPopulation(n: int, k: int, selected, rng):
    def crossoverOfChromosomes(n: int, solA: tuple, solB: tuple):
        def crossoverOX1(n:int, pos1: int, pos2: int, mainParentOrder, sideParentOrder):
            childOrder = np.full(n, np.nan, int)
            usedIdSet = set()

            for i in range(pos1, pos2):
                childOrder[i] = mainParentOrder[i]
                usedIdSet.add(mainParentOrder[i])

            indices = np.empty(n, dtype=int)
            indices[:n - pos2] = np.arange(start=pos2, stop=n) 
            indices[n - pos2:] = np.arange(pos2) 
            cur = 0
        
            for i in indices:
                curPosInChildOrder = indices[cur]
                if sideParentOrder[i] not in usedIdSet:
                    # print(curPosInChildOrder, i)
                    childOrder[curPosInChildOrder] = sideParentOrder[i]
                    cur += 1
                    usedIdSet.add(sideParentOrder[i])
                elif curPosInChildOrder == pos1:
                    break
            return childOrder

        #odabiru se dvije pozicije koje određuju segment u order listama
        [pos1, pos2] = np.random.randint(0, n, 2)
        if pos2 < pos1:
            tmp = pos1
            pos1 = pos2
            pos2 = tmp

        #kopiranje listi roditelja
        [realOrderA, realEncA] = solA
        [realOrderB, realEncB] = solB
        orderA = realOrderA.copy()
        orderB = realOrderB.copy()
        encA = realEncA.copy()
        encB = realEncB.copy()

        childAord = crossoverOX1(n, pos1, pos2, orderA, orderB)
        childBord = crossoverOX1(n, pos1, pos2, orderB, orderA)
        return ((childAord, encA), (childBord, encB))

    newGeneration = np.empty(n, dtype=object)
    cur = 0
    while cur < n:
        indices = rng.choice(k, n//2 + 1, replace=True)
        for i in range(k):
            solA = selected[indices[i]]
            solB = selected[indices[i + 1]]
            solC, solD = crossoverOfChromosomes(n, solA, solB)
            newGeneration[cur] = solC
            cur += 1
            if cur == n:
                return newGeneration
            newGeneration[cur] = solD
            cur += 1
            if cur == n:
                return newGeneration
    return newGeneration

# 1) k je veličina populacije za križanje
def geneticAlgorithm(n: int, k: int, numOfIter: int, matrix):
    generation = np.array([helper.getRandomStartingSolution(n) for _ in range(n)], dtype=object)
    line = np.empty(n, dtype=object)
    selected = np.empty(k, dtype=object)
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
        generation = crossoverOfSelectedPopulation(n, k, selected, rng)
        generation = mutateGeneration(n, generation, rng)        
    for i in range(n):
        assert len(generation) == n
        sol = generation[i]
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            bestSol = sol
    return (bestSol, bestFit)
