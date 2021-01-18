import numpy as np
import hc
import ga
import helper


# 1) Koliko treba biti susjedstvo?
# 2) Susjedstvo mozemo mijenjati takoder da mijenjamo i granice mozda
# 3) Mislim da je bolje kada mijenjamo i granice
def getHCNeighbourhood(n: int, sol: tuple):
    order, enc = sol
    newOrder = order.copy()
    newEnc = enc.copy()
    neigh = []
    swapPairs = np.random.randint(0, n, 2 * n)
    changeWhat = np.random.randint(0, 2, n)
    encToChange = np.random.randint(0, len(enc), 2 * n)
    for i in range(n):
        if changeWhat[i] == 0 or encToChange[i] == encToChange[i + 1]:
            newOrder = helper.swap(newOrder, swapPairs[i], swapPairs[i + 1])
            newSol = (newOrder, enc)
            neigh.append(newSol)
            newOrder = order.copy()
        else:
            newEnc = helper.changeEnc(newEnc, encToChange[i], encToChange[i + 1])
            newSol = (order, newEnc)
            neigh.append(newSol)
            newEnc = enc.copy()
    return neigh

# 1) repeat parametar je koliko puta da se ponovi algoritam pa onda uzmemo najbolje rješenje
def hillClimbing(n: int, repeat: int, matrix):
    retSol = None
    retFit = 0

    for _ in range(repeat): #koliko puta zelimo poceti ispocetka s random pocetnim rjesenjem
        bestSol = helper.getRandomStartingSolution(n)
        bestFit = helper.getFitnessOfSolution(bestSol, matrix)

        for _ in range(n*n): #koliko puta ponavljamo glavni dio hc
            neigh = getHCNeighbourhood(n, bestSol)

            for j in range(len(neigh)):
                curSol = neigh[j]
                curFit = helper.getFitnessOfSolution(curSol, matrix)
                if curFit > bestFit:
                    assert curFit == helper.getFitnessOfSolution(curSol, matrix)
                    bestFit = curFit
                    bestSol = curSol
        if retSol == None or bestFit > retFit:
            assert bestFit == helper.getFitnessOfSolution(bestSol, matrix)
            retSol = bestSol
            retFit = bestFit
    return (retSol, retFit)
