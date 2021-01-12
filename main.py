import numpy as np
import hc
import ga
import helper

# 1) Kako rijesiti problem lanaca vs ciklusa, tj. kako znati kada je jedno kada drugo
# 2) Za sada rijesavam kao da nema lanaca

def getMatrix(n: int):
    matrix = np.random.rand(n, n)
    return matrix

def loadMatrix(fileName: str):
    matrix = []
    with open(fileName) as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-2]
            arr = [int(n) for n in line.split(",")]
            matrix.append(arr)
    return matrix

def get01Matrix(matrix: np.array, cut: float):
    def cutFunction(x):
        if x < cut:
            return 0
        else:
            return 1
    return np.vectorize(cutFunction)(matrix)


# Ovdje upisujemo parametre
# n -> veličina matrice
# cut -> koliko dobra mora biti šansa za uspijeh transplatacije da bi je obavili
n = 99
matrix = loadMatrix("Matrica_100")
matrix = getMatrix(n)
cut = 0.60
matrix01 = get01Matrix(matrix, cut)

# rsol, rfit = hc.hillClimbing(n, 1, matrix01)

#TODO: ne znam koliko je najbolje da je k
k = 99 #k-> veličina selektirane populacije za krizanje
numOfIter = 500
rsol, rfit = ga.geneticAlgorithm(n, k, numOfIter, matrix01)
# print("------------------------------------------------")
# print(rsol)
print(helper.getDrawnSolution(rsol))
print(rfit)
# print(helper.getFitnessOfSolution(rsol, matrix01))
# print(matrix01)
# sol, fit = helper.getFitnessOfDrawnSolution(helper.getDrawnSolution(sol), matrix01)