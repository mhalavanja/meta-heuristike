import numpy as np
import hc
import ga
import helper

# 1) Kako rijesiti problem lanaca vs ciklusa, tj. kako znati kada je jedno kada drugo
# 2) Za sada rijesavam kao da nema lanaca

def getMatrix(n: int):
    matrix = np.random.rand(n, n)
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
n = 30
matrix = getMatrix(n)
cut = 0.5
matrix01 = get01Matrix(matrix, cut)

sol, fit = hc.hillClimbing(n, 5, matrix01)
print(helper.getDrawnSolution(sol))
print(fit)

k = 10
numOfIter = 20
sol, fit = ga.geneticAlgorithm(n, k, numOfIter, matrix01)
print(helper.getDrawnSolution(sol))
print(fit)