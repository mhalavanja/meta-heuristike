import numpy as np
# Kako rijesiti problem lanaca vs ciklusa

def getMatrix(n: int):
    matrix = np.random.rand(n, n)
    # print(type(matrix))
    return matrix

def get01Matrix(matrix: np.array, cut: float):
    def cutFunction(x):
        if x < cut:
            return 0
        else:
            return 1
    return np.vectorize(cutFunction)(matrix)

def getDrawnSolution(sol: tuple):
    order, enc = sol
    ret = []
    cur = 0
    for ntup in enc:
        tup = [order[cur + i] for i in range(ntup)]
        ret.append(tup)
        cur += ntup
    return ret

def getStartingSolution(n: int):
    l = []
    enc = [] #enclosure
    sum = 0
    while sum < n:
        [t] = np.random.randint(1, 4, 1)
        sum += t
        if sum > n:
            t = t - (sum - n)
            if t <= 0:
                break
        # print(sum)
        enc.append(t)
    for i in range(n):
        l.append(i)
    return (np.random.permutation(l), enc)

def getFitnessOfSolution(sol: tuple, matrix: np.array):
    order, enc = sol
    fit = 0
    cur = 0
    for l in enc:
        ntup = order[cur : cur + l]
        ntupWorks = True
        for i in range(l):
            a = ntup[i]
            b = None
            if i == l - 1:
                b = ntup[0]
            else:
                b = ntup[i + 1]
            if matrix[a][b] == 0:
                ntupWorks = False
            # print(a, b, matrix[a][b])
        if ntupWorks:
            fit += l
        cur += l
    return fit

def getFitnessOfDrawnSolution(sol: np.array, matrix: np.array):
    fit = 0
    for ntup in sol:
        l = len(ntup)
        ntupWorks = True
        for i in range(l):
            a = ntup[i]
            b = None
            if i == l - 1:
                b = ntup[0]
            else:
                b = ntup[i + 1]
            if matrix[a][b] == 0:
                ntupWorks = False
            # print(a, b, matrix[a][b])
        if ntupWorks:
            fit += l
    return fit

# 1) Koliko treba biti susjedstvo?
# 2) Susjedstvo mozemo mijenjati takoder da mijenjamo i granice mozda
def getHCNeighbourhood(sol: tuple):
    def swap(lista, i, j):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp
        return lista

    order, enc = sol
    neigh = []
    swapPairs = np.random.randint(0, n, 2 * n)
    # print(len(swapPairs))
    for i in range(n):
        # print(swapPairs[i], swapPairs[i + 1])
        # print(order)
        neigh.append(swap(order, swapPairs[i], swapPairs[i + 1]))
    return neigh

def hillClimbing(n: int, sol: tuple, matrix: np.array):
    order, enc = sol
    bestSol = sol
    bestFit = getFitnessOfSolution(sol, matrix)
    for __ in range(10*n):
        neigh = getHCNeighbourhood(bestSol)
        for x in neigh:
            # print(x)
            curFit = getFitnessOfSolution((x,enc), matrix)
            if(curFit >= bestFit):
                bestFit = curFit
                bestSol = (x, enc)
    return (bestSol, bestFit)

n = 10
matrix = getMatrix(n)
cut = 0.5
matrix01 = get01Matrix(matrix, cut)
sol = getStartingSolution(n)
# fitDrawn = getFitnessOfDrawnSolution(getDrawnSolution(sol), matrix01)
# print(fitDrawn)
fit = getFitnessOfSolution(sol, matrix01)
print(fit)
print(getDrawnSolution(sol))
bestSol, bestFit = hillClimbing(n, sol, matrix01)
print(bestFit)
print(getDrawnSolution(bestSol))
# print(getDrawnSolution(sol))