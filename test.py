import numpy as np
import helper
import ga 

def getTestMatrix(numOfPairs: int, fit: int):
    matrix = np.full((numOfPairs,numOfPairs), 0)
    enc = helper.getEnclousure(numOfPairs)
    rng = np.random.default_rng()
    idList = rng.choice(numOfPairs, fit, replace=False)
    cur = 0
    for l in enc:
        for i in range(l):
            a = idList[cur + i]
            b = None
            if i == l - 1:
                b = idList[cur]
            else:
                b = idList[cur + i + 1]
            matrix[a][b] = 1
        cur += l
    return (matrix, (idList, enc))

numOfPairs = 50
optFit = numOfPairs

popSize = 2000
selectionSize = 300
orderMutateProb = 0.01
encMutateProb = 0.05
numOfIter = 800

# print(matrix01)
matrix01, optimalSol = getTestMatrix(numOfPairs, optFit)
print("Optimalni fit: ", optFit)
print("Optimalno rješenje: ", helper.getFinalDrawnSolution(optimalSol, matrix01))
print()

sol, fit = ga.geneticAlgorithm(popSize, numOfPairs, selectionSize, encMutateProb, encMutateProb, numOfIter, matrix01)
print("Dobiveni fit: ", fit)
print("Dobiveno rješenje: ", helper.getFinalDrawnSolution(sol, matrix01))