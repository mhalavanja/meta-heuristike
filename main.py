import numpy as np
import hc
import ga
import helper

# 1) Kako rijesiti problem lanaca vs ciklusa, tj. kako znati kada je jedno kada drugo
# 2) Za sada rijesavam kao da nema lanaca

def getMatrix(numOfPairs: int):
    matrix = np.random.rand(numOfPairs, numOfPairs)
    return matrix

def loadMatrix(fileName: str):
    matrix = []
    with open(fileName) as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-2]
            arr = [int(numOfPairs) for numOfPairs in line.split(",")]
            matrix.append(arr)
    return matrix

def get01Matrix(matrix: np.ndarray, cut: float):
    def cutFunction(x):
        if x < cut:
            return 0
        else:
            return 1
    return np.vectorize(cutFunction)(matrix)


# Ovdje upisujemo parametre
# numOfPairs -> veličina matrice
# cut -> koliko dobra mora biti šansa za uspijeh transplatacije da bi je obavili
numOfPairs = 100
matrix = loadMatrix("Matrica_100")
# matrix = getMatrix(numOfPairs)
# cut = 0.60
matrix01 = get01Matrix(matrix, 0)

# rsol, rfit = hc.hillClimbing(numOfPairs, 1, matrix01)

#TODO: ne znam koliko je najbolje da je selectionSize
selectionSize = 50 #selectionSize-> veličina selektirane populacije za krizanje
numOfIter = 500
popSize = 100
orderMutateProb = 0.1
encMutateProb = 0.2

sol, fit = ga.geneticAlgorithm(popSize, numOfPairs, selectionSize, encMutateProb, orderMutateProb, numOfIter, matrix01)
print(fit)
print(sol)