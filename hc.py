import helper

def hillClimbing(numOfPairs: int, repeat: int, matrix):
    retSol = None
    retFit = 0

    for _ in range(repeat):
        curSol = helper.getRandomStartingSolution(numOfPairs)
        curFit = helper.getFitnessOfSolution(curSol, matrix)
        lastFit = curFit - 1

        while lastFit < curFit:
            lastFit = curFit
            order, enc = curSol
            for i in range(numOfPairs):
                for j in range(i + 1, numOfPairs):
                    helper.swap(order, i, j)
                    newFit = helper.getFitnessOfSolution((order, enc), matrix)
                    if newFit > curFit:
                        curFit = newFit
                        curSol = (order.copy(), enc)
                    helper.swap(order, j, i)

            for i in range(len(enc)):
                for j in range(i + 1, len(enc)):
                    newEnc = enc.copy()
                    helper.changeEnc(newEnc, i, j)
                    newFit = helper.getFitnessOfSolution((order, newEnc), matrix)
                    if newFit > curFit:
                        curFit = newFit
                        curSol = (order, newEnc)
        if retSol == None or curFit > retFit:
            retSol = curSol
            retFit = curFit
    return retSol, retFit
