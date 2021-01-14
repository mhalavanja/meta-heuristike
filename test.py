import numpy as np
import helper
import ga 

def getTestMatrix(n: int, fit: int):
    matrix = np.full((n,n), 0)
    enc = helper.getEnclousure(n)
    rng = np.random.default_rng()
    idList = rng.choice(n, fit, replace=False)
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

n = 10
k = n//2 #k-> veličina selektirane populacije za krizanje
optFit = n
numOfIter = 1000


# print(matrix01)
matrix01, optimalSol = getTestMatrix(n, optFit)
print("Optimalni fit: ", optFit)
print("Optimalno rješenje: ", helper.getFinalDrawnSolution(optimalSol, matrix01))
print()

sol, fit = ga.geneticAlgorithm(n, k, numOfIter, matrix01)
print("Dobiveni fit: ", fit)
print("Dobiveno rješenje: ", helper.getFinalDrawnSolution(sol, matrix01))