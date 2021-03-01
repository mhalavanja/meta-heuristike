import helper
import numpy as np

def hillClimbing(numOfPairs: int, repeat: int, matrix):
    retOrd = np.empty(numOfPairs, dtype=np.int16)  # order dio svakog rješenja u generaciji
    retEnc = np.empty_like(retOrd)  # enc ...
    retEncLen = 0  # velicina svakog enc ...
    retFit = 0

    for _ in range(repeat):
        curOrd = np.random.permutation(np.int16(numOfPairs))
        curEnc, curEncLen = helper.getEnclousure(numOfPairs)

        curFit = helper.getFitnessOfSolution((curOrd, curEnc, curEncLen), matrix)
        lastFit = curFit - 1

        while lastFit < curFit:
            lastFit = curFit
            order = curOrd.copy().astype("int16")
            enc = curEnc.copy()
            encLen = curEncLen

            for i in range(numOfPairs):
                for j in range(i + 1, numOfPairs):
                    helper.swap(order, i, j)
                    newFit = helper.getFitnessOfSolution((order, enc, encLen), matrix)
                    if newFit > curFit:
                        curFit = newFit
                        curOrd = order.copy()
                        curEnc = enc.copy()
                        curEncLen = encLen
                        # assert curFit == helper.getFitnessOfSolution((curSol[0], curSol[1], curSol[2]), matrix)
                    helper.swap(order, j, i)

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
                        # assert curFit == helper.getFitnessOfSolution((curSol[0], curSol[1], curSol[2]), matrix)

        if retEncLen == 0 or curFit > retFit:
            retOrd = curOrd
            retEnc = curEnc
            retEncLen = curEncLen
            retFit = curFit
            # assert retFit == helper.getFitnessOfSolution((retOrd, retEnc, retEncLen), matrix)
    return retOrd, retEnc, retEncLen, retFit
