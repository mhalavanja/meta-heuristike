import helper
import numpy as np

def hillClimbing(numOfPairs: int, repeat: int, matrix):
    #4 varijable koje određuju najbolje rješenje algoritma
    retOrd = np.empty(numOfPairs, dtype=np.int32)  # order dio svakog rješenja u generaciji
    retEnc = np.empty_like(retOrd)  # enc ...
    retEncLen = 0  # velicina svakog enc ...
    retFit = 0

    #broj ponavljanja za koji krećemo od početnog nasumičnog rješenja s algoritmom
    for _ in range(repeat):
        #trenutno rješenje u algoritmu
        curOrd = np.random.permutation(np.int32(numOfPairs))
        curEnc, curEncLen = helper.getEnclosure(numOfPairs)

        curFit = helper.getFitnessOfSolution((curOrd, curEnc, curEncLen), matrix)
        lastFit = curFit - 1

        while lastFit < curFit:
            lastFit = curFit

            #kopiramo početno rješenje trenutne iteracije koju zatim mjenjamo
            order = curOrd.copy().astype("int32")
            enc = curEnc.copy()
            encLen = curEncLen

            #prvi način generiranja susjedstva zamijenom u order listi
            for i in range(numOfPairs):
                for j in range(i + 1, numOfPairs):
                    #susjedstvo ne generiramo eksplicitno, nego svako rješenje iz
                    # susjedstva provjerimo pa vratimo na početno
                    helper.swap(order, i, j)
                    newFit = helper.getFitnessOfSolution((order, enc, encLen), matrix)
                    if newFit > curFit:
                        curFit = newFit
                        curOrd = order.copy()
                        curEnc = enc.copy()
                        curEncLen = encLen
                    helper.swap(order, j, i)

            #drugi način generiranja susjedstva promjenama u encloseurs listi
            for i in range(encLen):
                for j in range(i + 1, encLen):
                    newEnc = enc.copy()
                    newEncLen = helper.changeEnc(newEnc, encLen, i, j)
                    newFit = helper.getFitnessOfSolution((order, newEnc, newEncLen), matrix)
                    if newFit > curFit:
                        curFit = newFit
                        curOrd = order.copy()
                        curEnc = enc.copy()
                        curEncLen = encLen

        #ako je rješenje trenutnog ponavljanja najbolje, postaje novo rješenje koje vraćamo
        if retEncLen == 0 or curFit > retFit:
            retOrd = curOrd
            retEnc = curEnc
            retEncLen = curEncLen
            retFit = curFit
    return retOrd, retEnc, retEncLen, retFit
