import numpy as np
import helper
import numba as nb
from numba import njit


@njit
def SUSSelection(genOrd: np.ndarray, genEnc: np.ndarray, genEncLen: np.ndarray, line: np.ndarray, fitSum: int,
                 selectionSize: int, numOfPairs: int):
    selectOrd = np.empty((selectionSize, numOfPairs), dtype=np.int32)
    selectEnc = np.empty_like(selectOrd)
    selectEncLen = np.empty(selectionSize, dtype=np.int32)

    #ako je suma fitnessa svih rješenja jednaka nula, svejedno je koja rješenja odabiremo
    if fitSum == 0:
        return genOrd[:selectionSize], genEnc[:selectionSize], genEncLen[:selectionSize]

    p = fitSum/float(selectionSize)
    [start] = np.random.uniform(0, p, 1)
    curSol = 0
    curPoint = 0

    #ako trenutna točka nije između početne i krajnje točke trenutnog rješenja, povećamo trenutno rješenje koje gledamo,
    # a ako je, to je rješenje odabrano i gledamo sljedeću točku
    while curPoint < selectionSize:
        curPointer = start + float(curPoint * p)
        if line[curSol] <= curPointer < line[curSol + 1]:
            selectOrd[curPoint] = genOrd[curSol]
            selectEnc[curPoint] = genEnc[curSol]
            selectEncLen[curPoint] = genEncLen[curSol]
            curPoint += 1
        else:
            curSol += 1

    return selectOrd, selectEnc, selectEncLen

@njit
def topSelection(genOrd: np.ndarray, genEnc: np.ndarray, genEncLen: np.ndarray, fitnes: np.ndarray,
                 selectionSize: int, popSize: int):
    inds = np.argsort(fitnes)[popSize - selectionSize:]
    return genOrd[inds], genEnc[inds], genEncLen[inds]

@njit(nb.int32(nb.int32[:], nb.int32))
def mutateEnc(enc: np.ndarray, encLen: int):
    encToChange = np.random.choice(encLen, 2, replace=False)
    return helper.changeEnc(enc, encLen, encToChange[0], encToChange[1])


@njit((nb.int32, nb.int32[:]))
def mutateOrder(numOfPairs: int, order: np.ndarray):
    orderToChange = np.random.choice(numOfPairs, 2, replace=False)
    helper.swap(order, orderToChange[0], orderToChange[1])

@njit(parallel=True)
def mutateGeneration(genOrd, genEnc, genEncLen, popSize: int, numOfPairs: int, encMutateProb: float,
                     orderMutateProb: float):

    #kako bi imali podršku numba librarya, morali smo malo prilagoditi kod
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
@njit(nb.int32[:](nb.int32, nb.int32, nb.int32, nb.int32[:], nb.int32[:]))
def crossoverOX1(numOfPairs:int, pos1: int, pos2: int, mainParentOrder, sideParentOrder):
    childOrder = np.empty_like(mainParentOrder)
    usedIdSet = set()

    #početno prepisivanje iz glavnog roditelja u dijete
    for i in range(pos1, pos2):
        childOrder[i] = mainParentOrder[i]
        usedIdSet.add(mainParentOrder[i])

    #pomoćna lista indeksa koje moramo popuniti u djetetu točno ovim redom
    indices = np.empty(numOfPairs, dtype=np.int32)
    indices[:numOfPairs - pos2] = np.arange(pos2, numOfPairs)
    indices[numOfPairs - pos2:] = np.arange(pos2)

    #popunjavanje preostalih indeksa iz sporednog roditelja
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

@njit((nb.types.Tuple((nb.types.Tuple((nb.int32[:], nb.int32[:])), nb.types.Tuple((nb.int32[:], nb.int32[:])))))          (nb.int32, nb.int32[:], nb.int32[:], nb.int32[:], nb.int32[:]))
def crossoverOfChromosomes(numOfPairs: int, ordA: np.ndarray, encA: np.ndarray, ordB: np.ndarray, encB: np.ndarray):

    #odabiru se dvije pozicije koje određuju segment u order listama
    [pos1, pos2] = np.random.choice(numOfPairs, 2, replace=False)
    if pos2 < pos1:
        tmp = pos1
        pos1 = pos2
        pos2 = tmp

    #kopiranje listi roditelja kako ne bi promijenili trenutnu selektiranu populaciju koja se križa
    orderA = ordA.copy()
    orderB = ordB.copy()
    encA = encA.copy()
    encB = encB.copy()

    childAord = crossoverOX1(numOfPairs, pos1, pos2, orderA, orderB)
    childBord = crossoverOX1(numOfPairs, pos1, pos2, orderB, orderA)
    return (childAord, encA), (childBord, encB)

@njit((nb.types.Tuple((nb.int32[:,:], nb.int32[:,:], nb.int32[:])))(nb.int32, nb.int32, nb.int32, nb.int32[:,:], nb.int32[:,:], nb.int32[:]), parallel=True)
def crossoverOfSelectedPopulation(popSize: int, numOfPairs: int, selectionSize: int, selectOrd,
                                  selectEnc, selectEncLen):
    newGenOrd = np.empty((popSize, numOfPairs), dtype=np.int32)
    newGenEnc = np.empty_like(newGenOrd)
    newGenEncLen = np.empty(popSize, dtype=np.int32)

    k = popSize // 2
    indices = np.random.choice(selectionSize, popSize) #indeksi koji označavaju koje će se jedinke križati
    for i in nb.prange(k):
        j = k + i
        ind1 = indices[i]
        ind2 = indices[j]
        solC, solD = crossoverOfChromosomes(numOfPairs, selectOrd[ind1],
                                            selectEnc[ind1], selectOrd[ind2], selectEnc[ind2])

        newGenOrd[i], newGenEnc[i] = solC
        newGenEncLen[i] = selectEncLen[ind1]

        newGenOrd[j], newGenEnc[j] = solD
        newGenEncLen[j] = selectEncLen[ind2]

    return newGenOrd, newGenEnc, newGenEncLen

@njit(nb.types.Tuple((nb.int32[:], nb.int32[:], nb.int32, nb.int32))(nb.int32, nb.int32, nb.int32, nb.float32, nb.float32, nb.int32, nb.int32[:,:], nb.types.unicode_type))
def geneticAlgorithm(popSize: int, numOfPairs: int, selectionSize: int, encMutateProb: float, orderMutateProb: float,
                     numOfIter: int, matrix, selectionMode):
    #malo "varanje" kako bi si olakšali kasniju implementaciju
    if popSize % 2 == 1:
        popSize += 1
    if selectionSize % 2 == 1:
        selectionSize += 1

    genOrd = np.empty((popSize, numOfPairs), dtype=np.int32)  #order dio svakog rješenja u generaciji
    genEnc = np.empty_like(genOrd)  #enc ...
    genEncLen = np.empty(popSize, dtype=np.int32)  #velicina svakog enc ...

    #zadavanje nasumičnih početnih rješenja
    for i in range(popSize):
        genOrd[i] = np.random.permutation(numOfPairs)
        genEnc[i], genEncLen[i] = helper.getEnclosure(numOfPairs)

    #liste koje će označavati selektiranu populaciju
    selectOrd = np.empty((numOfPairs, selectionSize), dtype=np.int32) #order dio svakog rješenja za krizanje
    selectEnc = np.empty_like(selectOrd) #enc ...
    selectEncLen = np.empty(selectionSize, dtype=np.int32) #enc ...

    #line predstavlja rješenja na brojevnom pravcu što koristimo za SUS selekciju
    line = np.empty(popSize + 1, dtype=np.int32)
    fitnes = np.empty(popSize, dtype=np.int32)

    #varijable koje vraćamo na kraju algoritma koje označuju najbolje rješenje
    bestFit = 0
    bestSolOrd = np.empty(numOfPairs, dtype=np.int32)
    bestSolEnc = np.empty_like(bestSolOrd)
    bestSolEncLen = 0
    firstBestIt = 0

    for it in range(numOfIter):
        fitSum = 0
        line[0] = 0

        #fitness svakog rješenja nam treba za obje selekcije pa pošto ih već računamo, ako postoji novo najbolje
        # rješenje, spremimo ga
        for i in range(popSize):
            sol = (genOrd[i], genEnc[i], genEncLen[i])
            fit = helper.getFitnessOfSolution(sol, matrix)
            if fit > bestFit:
                bestFit = fit
                firstBestIt = it
                bestSolOrd = sol[0].copy()
                bestSolEnc = sol[1].copy()
                bestSolEncLen = sol[2]
            fitSum = fitSum + fit
            line[i + 1] = fitSum
            fitnes[i] = fit

        if selectionMode == "sus":
            selectOrd, selectEnc, selectEncLen = SUSSelection(genOrd, genEnc, genEncLen,
                         line, fitSum, selectionSize, numOfPairs)
        elif selectionMode == "top":
            selectOrd, selectEnc, selectEncLen = topSelection(genOrd, genEnc, genEncLen, fitnes, selectionSize, popSize)

        genOrd, genEnc, genEncLen = crossoverOfSelectedPopulation(popSize, numOfPairs, selectionSize,
                                                                  selectOrd, selectEnc, selectEncLen)
        mutateGeneration(genOrd, genEnc, genEncLen, popSize, numOfPairs, encMutateProb, orderMutateProb)

    #provjerimo je li najbolje rješenje možda u zadnjoj generaciji
    for i in range(popSize):
        sol = (genOrd[i], genEnc[i], genEncLen[i])
        fit = helper.getFitnessOfSolution(sol, matrix)
        if fit > bestFit:
            bestFit = fit
            firstBestIt = numOfIter
            bestSolOrd = sol[0].copy()
            bestSolEnc = sol[1].copy()
            bestSolEncLen = sol[2]

    print("Prvi put najbolje rješenje: ", firstBestIt)
    return bestSolOrd, bestSolEnc, bestSolEncLen, bestFit