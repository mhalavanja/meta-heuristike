import numpy as np
import helper
import ga 

def getTestMatrix(numOfPairs: int, fit: int):
    matrix = np.full((numOfPairs,numOfPairs), 0)
    enc = helper.getEnclousure(numOfPairs)
    rng = np.random.default_rng()
    idList = rng.choice(numOfPairs, fit, replace=False)
    # curFit = 0
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

numOfPairs = 10
selectionSize = numOfPairs//2 #selectionSize-> veličina selektirane populacije za krizanje
optFit = numOfPairs
numOfIter = 1000
popSize = 500
orderMutateProb = 0.1
encMutateProb = 0.2

# print(matrix01)
matrix01, optimalSol = getTestMatrix(numOfPairs, optFit)
print("Optimalni fit: ", optFit)
print("Optimalno rješenje: ", helper.getFinalDrawnSolution(optimalSol, matrix01))
print()

sol, fit = ga.geneticAlgorithm(popSize, numOfPairs, selectionSize, encMutateProb, encMutateProb, numOfIter, matrix01)
print("Dobiveni fit: ", fit)
print("Dobiveno rješenje: ", helper.getFinalDrawnSolution(sol, matrix01))