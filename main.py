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
n = 50
matrix = getMatrix(n)
cut = 0.5
matrix01 = get01Matrix(matrix, cut)

# sol, fit = hc.hillClimbing(n, 3, matrix01)
# print(helper.getDrawnSolution(sol))
# print(fit)

#TODO: ne znam koliko je najbolje da je k
k = 10 #k-> veličina selektirane populacije za krizanje
numOfIter = 500
sol, fit = ga.geneticAlgorithm(n, k, numOfIter, matrix01)
print(helper.getDrawnSolution(sol))
print(fit)