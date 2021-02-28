import numpy as np
import helper
import numba as nb
from numba import jit, njit

# @jit
# def SUSSelection(genOrd, genEnc, genEncLen, selectOrd, selectEnc, selectEncLen, line, fitSum: int, popSize: int, selectionSize: int):
#     if fitSum == 0:
#         selectOrd = genOrd[:selectionSize]
#         selectEnc = genEnc[:selectionSize]
#         selectEncLen = genEncLen[:selectionSize]
#         return
#     p = fitSum/float(selectionSize)
#     [r] = np.random.uniform(0, p, 1)
#     j = 0
#     curPointer = r
#     cur = 0
#     while curPointer < line[0][0]:
#             j += 1
#             curPointer = r + float(j * p)
#     for i in range(popSize):    
#         while curPointer > line[i][0] and curPointer < line[i][1]:
#             selectOrd[cur] = genOrd[i]
#             selectEnc[cur] = genEnc[i]
#             selectEncLen[cur] = genEncLen[i]
#             cur += 1
#             j += 1
#             curPointer = r + float(j * p)
#     return

#@jit
# def topSelection(generation, fitnes, selectionSize: int):
#     inds = np.array(fitnes).argsort()[::-1] 
#     generation = np.array(generation, tuple)[inds]
#     return generation[:selectionSize]

# @njit(nb.types.Tuple((nb.int16, nb.int16))(nb.int16, nb.int16))
# def get2Random(fr: int, to: int):
#     i = np.random.randint(fr, to)
#     j = np.random.randint(fr, to)
#     while i == j:
#         j = np.random.randint(fr, to)
#     return i, j

@njit(nb.int16(nb.int16[:], nb.int16))
def mutateEnc(enc: np.ndarray, encLen: int):
    encToChange = np.random.choice(encLen, 2, replace=False)
    return helper.changeEnc(enc, encLen, encToChange[0], encToChange[1])
    # i, j = get2Random(0, encLen)
    # return helper.changeEnc(enc, encLen, i, j)

@njit((nb.int16, nb.int16[:]))
def mutateOrder(numOfPairs: int, order: np.ndarray):
    orderToChange = np.random.choice(numOfPairs, 2, replace=False)
    helper.swap(order, orderToChange[0], orderToChange[1])
    # i, j = get2Random(0, numOfPairs)
    # helper.swap(order, i, j)
    return

@njit(parallel=True)
def mutateGeneration(genOrd, genEnc, genEncLen, popSize: int, numOfPairs: int, encMutateProb: float, orderMutateProb: float):
    mut = np.random.randint(0, 100, 2 * popSize)
    mutEnc = encMutateProb * 100
    mutOrd = orderMutateProb * 100

    for i in nb.prange(popSize):
        if mut[i] < mutEnc:
            genEncLen[i] = mutateEnc(genEnc[i], genEncLen[i])

    for i in nb.prange(popSize):
        if mut[popSize + i] < mutOrd:
            mutateOrder(numOfPairs, genOrd[i])

    return

#Koristimo križanje poretka (OX1) zato što je bitan redosljed u kojem su brojevi, a ne 
#njihov apsolutni poredak u listi

@njit(nb.int16[:](nb.int16, nb.int16, nb.int16, nb.int16[:], nb.int16[:]))
def crossoverOX1(numOfPairs:int, pos1: int, pos2: int, mainParentOrder, sideParentOrder):
    childOrder = np.empty_like(mainParentOrder)
    usedIdSet = set()

    for i in range(pos1, pos2):
        childOrder[i] = mainParentOrder[i]
        usedIdSet.add(mainParentOrder[i])

    indices = np.empty(numOfPairs, dtype=np.short)
    indices[:numOfPairs - pos2] = np.arange(pos2, numOfPairs)
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

@njit((nb.types.Tuple((nb.types.Tuple((nb.int16[:], nb.int16[:])), nb.types.Tuple((nb.int16[:], nb.int16[:])))))
          (nb.int16, nb.int16[:], nb.int16[:], nb.int16[:], nb.int16[:]))
def crossoverOfChromosomes(numOfPairs: int, ordA: np.ndarray, encA: np.ndarray, ordB: np.ndarray, encB: np.ndarray):

    #odabiru se dvije pozicije koje određuju segment u order listama
    [pos1, pos2] = np.random.choice(numOfPairs, 2, replace=False)
    # pos1, pos2 = get2Random(0, numOfPairs)
    if pos2 < pos1:
        tmp = pos1
        pos1 = pos2
        pos2 = tmp

    #kopiranje listi roditelja
    orderA = ordA.copy()
    orderB = ordB.copy()
    encA = encA.copy()
    encB = encB.copy()

    childAord = crossoverOX1(numOfPairs, pos1, pos2, orderA, orderB)
    childBord = crossoverOX1(numOfPairs, pos1, pos2, orderB, orderA)
    return (childAord, encA), (childBord, encB)

@njit((nb.types.Tuple((nb.int16[:,:], nb.int16[:,:], nb.int16[:])))
          (nb.int16, nb.int16, nb.int16, nb.int16[:,:], nb.int16[:,:], nb.int16[:]))
def crossoverOfSelectedPopulation(popSize: int, numOfPairs: int, selectionSize: int, selectOrd, selectEnc, selectEncLen):
    
    newGenOrd = np.empty((popSize, numOfPairs), dtype=np.short)
    newGenEnc = np.empty_like(newGenOrd)
    newGenEncLen = np.empty(popSize, dtype=np.short)
    cur = 0

    while cur < popSize:
        indices = np.random.choice(selectionSize, popSize//2 + 1)
        for i in range(selectionSize):
            ind = indices[i]
            ind1 = indices[i + 1]

            solC, solD = crossoverOfChromosomes(numOfPairs, selectOrd[ind],
                                                selectEnc[ind], selectOrd[ind1], selectEnc[ind1])
            
            newGenOrd[cur] = solC[0]
            newGenEnc[cur] = solC[1]
            newGenEncLen[cur] = selectEncLen[ind]

            cur += 1
            if cur == popSize:
                return newGenOrd, newGenEnc, newGenEncLen

            newGenOrd[cur] = solD[0]
            newGenEnc[cur] = solD[1]
            newGenEncLen[cur] = selectEncLen[ind1]

            cur += 1
            if cur == popSize:
                return newGenOrd, newGenEnc, newGenEncLen
    return newGenOrd, newGenEnc, newGenEncLen

@njit(nb.types.Tuple((nb.int16[:], nb.int16[:], nb.int16, nb.int16))
         (nb.int16, nb.int16, nb.int16, nb.float32, nb.float32, nb.int16, nb.int16[:,:], nb.types.unicode_type))
def geneticAlgorithm(popSize: int, numOfPairs: int, selectionSize: int, encMutateProb: float, orderMutateProb: float,  numOfIter: int, matrix, selectionMode):
    genOrd = np.empty((popSize, numOfPairs), dtype=np.short)  #order dio svakog rješenja u generaciji
    genEnc = np.empty_like(genOrd)  #enc ...
    genEncLen = np.empty(popSize, dtype=np.short)  #velicina svakog enc ...

    i = 0
    for i in nb.prange(popSize):
        genOrd[i] = np.random.permutation(numOfPairs)
        genEnc[i], genEncLen[i] = helper.getEnclousure(numOfPairs)

    selectOrd = np.empty((numOfPairs, selectionSize), dtype=np.short) #order dio svakog rješenja za krizanje
    selectEnc = np.empty_like(selectOrd) #enc ...
    selectEncLen = np.empty(selectionSize, dtype=np.short) #enc ...

    # line = np.empty(popSize, dtype=np.short)
    fitnes = np.empty(popSize, dtype=np.short)

    bestFit = 0
    bestSolOrd = np.empty(numOfPairs, dtype=np.short)
    bestSolEnc = np.empty_like(bestSolOrd)
    bestSolEncLen = 0

    for _ in range(numOfIter):    
        fitSum = 0
        for i in range(popSize):
            # assert sum(genEnc[i][:genEncLen[i]]) == numOfPairs
            sol = (genOrd[i], genEnc[i], genEncLen[i])
            fit = helper.getFitnessOfSolution(sol, matrix)
            if fit > bestFit:
                bestFit = fit
                bestSolOrd = sol[0].copy()
                bestSolEnc = sol[1].copy()
                bestSolEncLen = sol[2]
                # assert helper.getFitnessOfSolution(bestSol, matrix) == bestFit
            newFitSum = fitSum + fit
            # line[i] = (fitSum, newFitSum)
            fitSum = newFitSum
            fitnes[i] = fit
            # assert sum(genEnc[i][:genEncLen[i]]) == numOfPairs
        # if selectionMode == "sus":
        #     SUSSelection(genOrd, genEnc, genEncLen, selectOrd,
        #         selectEnc, selectEncLen, line, fitSum, popSize, selectionSize)
        # elif selectionMode == "top":
        if selectionMode == "top":
            inds = np.argsort(fitnes)[popSize - selectionSize:]
            selectOrd = genOrd[inds]
            selectEnc = genEnc[inds]
            selectEncLen = genEncLen[inds]

        genOrd, genEnc, genEncLen = crossoverOfSelectedPopulation(popSize, numOfPairs, selectionSize, selectOrd, selectEnc, selectEncLen)
        # print(bestFit, helper.getDrawnSolution(bestSol))
        # assert helper.getFitnessOfSolution(bestSol, matrix) == bestFit or _ == 0

        mutateGeneration(genOrd, genEnc, genEncLen, popSize, numOfPairs, encMutateProb, orderMutateProb)
        # print(bestFit, helper.getDrawnSolution(bestSol))
        # assert helper.getFitnessOfSolution(bestSol, matrix) == bestFit or _ == 0

    for i in range(popSize):
        sol = (genOrd[i], genEnc[i], genEncLen[i])
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            bestSolOrd = sol[0].copy()
            bestSolEnc = sol[1].copy()
            bestSolEncLen = sol[2]
            # assert helper.getFitnessOfSolution(bestSol, matrix) == bestFit

    return bestSolOrd, bestSolEnc, bestSolEncLen, bestFit