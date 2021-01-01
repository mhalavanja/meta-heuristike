import numpy as np
import hc
import ga
import helper


# 1) Koliko treba biti susjedstvo?
# 2) Susjedstvo mozemo mijenjati takoder da mijenjamo i granice mozda
# 3) Mislim da je bolje kada mijenjamo i granice
def getHCNeighbourhood(n: int, sol: tuple):
    order, enc = sol
    neigh = []
    swapPairs = np.random.randint(0, n, 2 * n)
    changeWhat = np.random.randint(0, 2, n)
    encToChange = np.random.randint(0, len(enc), 2 * n)
    for i in range(n):
        if changeWhat[i] == 0 or encToChange[i] == encToChange[i + 1]:
            neigh.append((helper.swap(order, swapPairs[i], swapPairs[i + 1]), enc))
        else:
            neigh.append((order, helper.changeEnc(enc, encToChange[i], encToChange[i + 1])))
    return neigh

# 1) repeat parametar je koliko puta da se ponovi algoritam pa onda uzmemo najbolje rješenje
def hillClimbing(n: int, repeat: int, matrix: np.array):
    retSol = None
    retFit = 0
    for __ in range(repeat): #koliko puta zelimo poceti ispocetka s random pocetnim rjesenjem
        bestSol = helper.getRandomStartingSolution(n)
        bestFit = helper.getFitnessOfSolution(bestSol, matrix)
        for __ in range(n*n): #koliko puta ponavljamo glavni dio hc
            neigh = getHCNeighbourhood(n, bestSol)
            for j in range(len(neigh)):
                curOrder = neigh[j][0]
                curEnc = neigh[j][1]
                curFit = helper.getFitnessOfSolution((curOrder,curEnc), matrix)
                if(curFit >= bestFit):
                    bestFit = curFit
                    bestSol = (curOrder, curEnc)
        if(retSol == None):
            retSol = bestSol
            retFit = bestFit
        elif(bestFit > retFit):
            retSol = bestSol
            retFit = bestFit
    return (retSol, retFit)
