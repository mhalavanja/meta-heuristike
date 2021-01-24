import numpy as np
import helper

# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
# Stochastic universal sampling
def SUSSelection(generation, line, fitSum: int, popSize: int, selectionSize: int):
    selected = np.empty(selectionSize, dtype=object)
    if fitSum == 0:
        return generation[:selectionSize].copy()
    p = fitSum/float(selectionSize)
    [r] = np.random.uniform(0, p, 1)
    j = 0
    curPointer = r
    cur = 0
    while curPointer < line[0][0]:
            j += 1
            curPointer = r + float(j * p)
    for i in range(popSize):    
        while curPointer > line[i][0] and curPointer < line[i][1]:
            selected[cur] = generation[i]
            cur += 1
            j += 1
            curPointer = r + float(j * p)
    assert None not in selected
    return selected

def topSelection(generation, fitnes, selectionSize: int):
    inds = np.array(fitnes).argsort()[::-1] 
    generation = np.array(generation, tuple)[inds]
    return generation[:selectionSize]

# 1) TODO: Mogli bi imati dvije mutacije, jedna mtuacija za order, druga za enc 
def mutateGeneration(popSize: int, numOfPairs: int, encMutateProb: float, orderMutateProb: float, generation, rng):
    def mutateEnc(sol: tuple, rng):
        order, enc = sol
        # newOrder = order.copy()
        # newEnc = enc.copy()
        encToChange = rng.choice(len(enc), 2, replace=False)
        return(order, helper.changeEnc(enc, encToChange[0], encToChange[1]))

    def mutateOrder(numOfPairs: int, sol: tuple, rng):
        order, enc = sol
        # newOrder = order.copy()
        # newEnc = enc.copy()
        orderToChange = rng.choice(numOfPairs, 2, replace=False)
        return(helper.swap(order, orderToChange[0], orderToChange[1]), enc)

    mutationEnc = np.random.choice(2, popSize, p=[1-encMutateProb, encMutateProb]) #mogucnost mutacije enclousera
    mutationOrder = np.random.choice(2, popSize, p=[1-orderMutateProb, orderMutateProb]) #mogucnost mutacije ordera
    
    for i in range(popSize):
        if mutationEnc[i] == 1:
            generation[i] = mutateEnc(generation[i], rng)
        if mutationOrder[i] == 1:
            generation[i] = mutateOrder(numOfPairs, generation[i], rng)
    return generation

# 1) Koristimo križanje poretka (OX1) zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossoverOfSelectedPopulation(popSize: int, numOfPairs: int, selectionSize: int, selected, rng):
    def crossoverOfChromosomes(numOfPairs: int, solA: tuple, solB: tuple, rng):
        def crossoverOX1(numOfPairs:int, pos1: int, pos2: int, mainParentOrder, sideParentOrder):
            childOrder = np.empty_like(mainParentOrder)
            usedIdSet = set()

            for i in range(pos1, pos2):
                childOrder[i] = mainParentOrder[i]
                usedIdSet.add(mainParentOrder[i])

            indices = np.empty(numOfPairs, dtype=int)
            indices[:numOfPairs - pos2] = np.arange(start=pos2, stop=numOfPairs) 
            indices[numOfPairs - pos2:] = np.arange(pos2) 
            cur = 0
        
            for i in indices:
                curPosInChildOrder = indices[cur]
                if sideParentOrder[i] not in usedIdSet:
                    childOrder[curPosInChildOrder] = sideParentOrder[i]
                    cur += 1
                    usedIdSet.add(sideParentOrder[i])
                elif curPosInChildOrder == pos1:
                    break
            return childOrder

        #odabiru se dvije pozicije koje određuju segment u order listama
        [pos1, pos2] = rng.choice(numOfPairs, 2, replace=False)
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

        childAord = crossoverOX1(numOfPairs, pos1, pos2, orderA, orderB)
        childBord = crossoverOX1(numOfPairs, pos1, pos2, orderB, orderA)
        return ((childAord, encA), (childBord, encB))

    newGeneration = np.empty(popSize, dtype=object)
    cur = 0
    while cur < popSize:
        indices = rng.choice(selectionSize, popSize//2 + 1, replace=True)
        for i in range(selectionSize):
            solA = selected[indices[i]]
            solB = selected[indices[i + 1]]
            solC, solD = crossoverOfChromosomes(numOfPairs, solA, solB, rng)
            newGeneration[cur] = solC
            cur += 1
            if cur == popSize:
                return newGeneration
            newGeneration[cur] = solD
            cur += 1
            if cur == popSize:
                return newGeneration
    return newGeneration

# 1) selectionSize je veličina populacije za križanje
def geneticAlgorithm(popSize: int, numOfPairs: int, selectionSize: int, encMutateProb: float, orderMutateProb: float,  numOfIter: int, matrix):
    generation = np.array([helper.getRandomStartingSolution(numOfPairs) for _ in range(popSize)], dtype=object)
    line = np.empty(popSize, dtype=object)
    selected = np.empty(selectionSize, dtype=object)
    fitnes = np.empty(popSize, dtype=int)
    rng = np.random.default_rng()
    bestFit = 0
    bestSol = None

    for __ in range(numOfIter):    
        assert len(generation) == popSize
        fitSum = 0

        for i in range(popSize):
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

        selected = SUSSelection(generation, line, fitSum, popSize, selectionSize)
        # selected = topSelection(generation, fitnes, selectionSize)
        generation = crossoverOfSelectedPopulation(popSize, numOfPairs, selectionSize, selected, rng)
        generation = mutateGeneration(popSize, numOfPairs, encMutateProb, orderMutateProb, generation, rng)        
    for i in range(popSize):
        assert len(generation) == popSize
        sol = generation[i]
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            bestSol = sol
    return (bestSol, bestFit)