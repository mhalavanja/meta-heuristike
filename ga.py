import numpy as np
import helper
import numba as nb
from numba import njit


@njit
def SUSSelection(genOrd: np.ndarray, genEnc: np.ndarray, genEncLen: np.ndarray, line: np.ndarray, fitSum: int,
                 popSize: int, selectionSize: int, numOfPairs: int):
    selectOrd = np.empty((popSize, numOfPairs), dtype=np.short) #order dio svakog rješenja za krizanje
    selectEnc = np.empty_like(selectOrd) #enc ...
    selectEncLen = np.empty(selectionSize, dtype=np.short) #enc ...

    if fitSum == 0:
        return genOrd[:selectionSize], genEnc[:selectionSize], genEncLen[:selectionSize]
    p = fitSum/float(selectionSize)
    [r] = np.random.uniform(0, p, 1)
    j = 0
    curPointer = r
    cur = 0
    for i in nb.prange(popSize + 1):
        while curPointer > line[i] and curPointer < line[i + 1]:
            selectOrd[cur] = genOrd[i]
            selectEnc[cur] = genEnc[i]
            selectEncLen[cur] = genEncLen[i]
            cur += 1
            j += 1
            curPointer = r + float(j * p)
    return selectOrd, selectEnc, selectEncLen

@njit
def topSelection(genOrd: np.ndarray, genEnc: np.ndarray, genEncLen: np.ndarray, fitnes: np.ndarray,
                 selectionSize: int, popSize: int):
    inds = np.argsort(fitnes)[popSize - selectionSize:]
    return genOrd[inds], genEnc[inds], genEncLen[inds]

@njit(nb.int16(nb.int16[:], nb.int16))
def mutateEnc(enc: np.ndarray, encLen: int):
    # print(encLen)
    encToChange = np.random.choice(encLen, 2, replace=False)
    return helper.changeEnc(enc, encLen, encToChange[0], encToChange[1])


@njit((nb.int16, nb.int16[:]))
def mutateOrder(numOfPairs: int, order: np.ndarray):
    # print(numOfPairs)
    orderToChange = np.random.choice(numOfPairs, 2, replace=False)
    helper.swap(order, orderToChange[0], orderToChange[1])

@njit(parallel=True)
def mutateGeneration(genOrd, genEnc, genEncLen, popSize: int, numOfPairs: int, encMutateProb: float,
                     orderMutateProb: float):
    mut = np.random.randint(0, 100, 2 * popSize)
    mutEnc = encMutateProb * 100
    mutOrd = orderMutateProb * 100

    for i in nb.prange(popSize):
        if mut[i] < mutEnc:
            genEncLen[i] = mutateEnc(genEnc[i], genEncLen[i])

    for i in nb.prange(popSize):
        if mut[popSize + i] < mutOrd:
            mutateOrder(numOfPairs, genOrd[i])

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

@njit((nb.types.Tuple((nb.types.Tuple((nb.int16[:], nb.int16[:])), nb.types.Tuple((nb.int16[:], nb.int16[:])))))          (nb.int16, nb.int16[:], nb.int16[:], nb.int16[:], nb.int16[:]))
def crossoverOfChromosomes(numOfPairs: int, ordA: np.ndarray, encA: np.ndarray, ordB: np.ndarray, encB: np.ndarray):

    #odabiru se dvije pozicije koje određuju segment u order listama
    # print(numOfPairs)
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

@njit((nb.types.Tuple((nb.int16[:,:], nb.int16[:,:], nb.int16[:])))(nb.int16, nb.int16, nb.int16, nb.int16[:,:], nb.int16[:,:], nb.int16[:]), parallel=True)
def crossoverOfSelectedPopulation(popSize: int, numOfPairs: int, selectionSize: int, selectOrd,
                                  selectEnc, selectEncLen):

    newGenOrd = np.empty((popSize, numOfPairs), dtype=np.short)
    newGenEnc = np.empty_like(newGenOrd)
    newGenEncLen = np.empty(popSize, dtype=np.short)
    k = popSize // 2
    indices = np.random.choice(selectionSize, popSize)
    for i in nb.prange(k):
        j = k + i
        ind1 = indices[i]
        ind2 = indices[j]
        solC, solD = crossoverOfChromosomes(numOfPairs, selectOrd[ind1],
                                            selectEnc[ind1], selectOrd[ind2], selectEnc[ind2])

        newGenOrd[i] = solC[0]
        newGenEnc[i] = solC[1]
        newGenEncLen[i] = selectEncLen[ind1]

        newGenOrd[j] = solD[0]
        newGenEnc[j] = solD[1]
        newGenEncLen[j] = selectEncLen[ind2]
    return newGenOrd, newGenEnc, newGenEncLen

@njit(nb.types.Tuple((nb.int16[:], nb.int16[:], nb.int16, nb.int16))(nb.int16, nb.int16, nb.int16, nb.float32, nb.float32, nb.int16, nb.int16[:,:], nb.types.unicode_type))
def geneticAlgorithm(popSize: int, numOfPairs: int, selectionSize: int, encMutateProb: float, orderMutateProb: float,
                     numOfIter: int, matrix, selectionMode):
    if popSize % 2 == 1:
        popSize += 1
    if selectionSize % 2 == 1:
        selectionSize += 1

    genOrd = np.empty((popSize, numOfPairs), dtype=np.short)  #order dio svakog rješenja u generaciji
    genEnc = np.empty_like(genOrd)  #enc ...
    genEncLen = np.empty(popSize, dtype=np.short)  #velicina svakog enc ...

    for i in range(popSize):
        genOrd[i] = np.random.permutation(numOfPairs)
        genEnc[i], genEncLen[i] = helper.getEnclousure(numOfPairs)

    selectOrd = np.empty((numOfPairs, selectionSize), dtype=np.short) #order dio svakog rješenja za krizanje
    selectEnc = np.empty_like(selectOrd) #enc ...
    selectEncLen = np.empty(selectionSize, dtype=np.short) #enc ...

    line = np.empty(popSize + 1, dtype=np.short)
    fitnes = np.empty(popSize, dtype=np.short)

    bestFit = 0
    bestSolOrd = np.empty(numOfPairs, dtype=np.short)
    bestSolEnc = np.empty_like(bestSolOrd)
    bestSolEncLen = 0

    for _ in range(numOfIter):
        fitSum = 0
        line[0] = 0
        for i in range(popSize):
            sol = (genOrd[i], genEnc[i], genEncLen[i])
            fit = helper.getFitnessOfSolution(sol, matrix)
            if fit > bestFit:
                bestFit = fit
                bestSolOrd = sol[0].copy()
                bestSolEnc = sol[1].copy()
                bestSolEncLen = sol[2]
            fitSum = fitSum + fit
            line[i + 1] = fitSum
            fitnes[i] = fit
        if selectionMode == "sus":
            selectOrd, selectEnc, selectEncLen = SUSSelection(genOrd, genEnc, genEncLen,
                         line, fitSum, popSize, selectionSize, numOfPairs)
        elif selectionMode == "top":
            selectOrd, selectEnc, selectEncLen = topSelection(genOrd, genEnc, genEncLen, fitnes, selectionSize, popSize)

        genOrd, genEnc, genEncLen = crossoverOfSelectedPopulation(popSize, numOfPairs, selectionSize,
                                                                  selectOrd, selectEnc, selectEncLen)
        mutateGeneration(genOrd, genEnc, genEncLen, popSize, numOfPairs, encMutateProb, orderMutateProb)

    for i in range(popSize):
        sol = (genOrd[i], genEnc[i], genEncLen[i])
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            bestSolOrd = sol[0].copy()
            bestSolEnc = sol[1].copy()
            bestSolEncLen = sol[2]

    return bestSolOrd, bestSolEnc, bestSolEncLen, bestFit