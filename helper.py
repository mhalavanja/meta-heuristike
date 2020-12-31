import numpy as np

# 1) Ova funkcija služi samo radi ljepšeg prikaza rješenja
def getDrawnSolution(sol: tuple):
    order, enc = sol
    ret = []
    cur = 0
    for ntup in enc:
        tup = [order[cur + i] for i in range(ntup)]
        ret.append(tup)
        cur += ntup
    return ret

# 1) Mislim da je ovo najfleksibilniji prikaz rješenja, zauzima duplo memorije, ali memorija nije probelm
def getRandomStartingSolution(n: int):
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
        enc.append(t)
    for i in range(n):
        l.append(i)
    return (np.random.permutation(l), enc)

# 1) Mozda da pocnemo s jednostavnim greedy algoritmom (GRASP)
# 2) Mislim da je pretesko ovo napraviti, a da ima koristi
def getGreedyStartingSolution(n: int, matrix: np.array):
    pass

# 1) Za svaki ciklus gleda je li svi u ciklusu imaju transplataciju i onda je fit += len(ciklusa)
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
                break
        if ntupWorks:
            fit += l
        cur += l
    return fit

# 1) Ovo nam vjerojatno ne treba, samo sam imao dvije implementacije na umu
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
        if ntupWorks:
            fit += l
    return fit

def swap(lista: np.array, i: int, j: int):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp
        return lista

def changeEnc(enc: np.array, i: int, j: int):
    a = enc[i]
    b = enc[j]
    if a != 1 and b != 3:
        enc[i] = a - 1
        enc[j] = b + 1
    elif a != 3 and b != 1:
        enc[i] = a + 1
        enc[j] = b - 1
    return enc
