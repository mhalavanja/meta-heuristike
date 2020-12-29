import numpy as np
# 1) Kako rijesiti problem lanaca vs ciklusa, tj. kako znati kada je jedno kada drugo
# 2) Za sada rijesavam kao da nema lanaca

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
        # print(sum)
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
    # print(order)
    # print(enc)
    for l in enc:
        ntup = order[cur : cur + l]
        # print(ntup, l)
        # print(enc)
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
            # print(a, b, matrix[a][b])
        if ntupWorks:
            fit += l
    return fit

# 1) Koliko treba biti susjedstvo?
# 2) Susjedstvo mozemo mijenjati takoder da mijenjamo i granice mozda
# 3) Mislim da je bolje kada mijenjamo i granice
def getHCNeighbourhood(sol: tuple):
    def swap(lista: np.array, i: int, j: int):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp
        return lista

    def changeEnc(enc: np.array, i: int, j: int):
        a = enc[i]
        b = enc[j]
        # print(i, j)
        # print("Pocetak: ", enc, sum(enc))
        if a != 1 and b != 3:
            enc[i] = a - 1
            enc[j] = b + 1
            # print("1: ", enc, sum(enc))
            # return enc
        elif a != 3 and b != 1:
            enc[i] = a + 1
            enc[j] = b - 1
        # print("2: ", enc, sum(enc))
        return enc

    order, enc = sol
    neigh = []
    swapPairs = np.random.randint(0, n, 2 * n)
    changeWhat = np.random.randint(0, 2, n)
    encToChange = np.random.randint(0, len(enc), 2 * n)
    # print(len(swapPairs))
    for i in range(n):
        # print(swapPairs[i], swapPairs[i + 1])
        # print(changeWhat[i])
        if changeWhat[i] == 0 or encToChange[i] == encToChange[i + 1]:
            neigh.append((swap(order, swapPairs[i], swapPairs[i + 1]), enc))
        else:
            neigh.append((order, changeEnc(enc, encToChange[i], encToChange[i + 1])))
    return neigh

# 1) repeat parametar je koliko puta da se ponovi algoritam pa onda uzmemo najbolje rješenje
def hillClimbing(n: int, repeat: int, matrix: np.array):
    retSol = None
    retFit = 0
    for __ in range(repeat):
        bestSol = getRandomStartingSolution(n)
        bestFit = getFitnessOfSolution(bestSol, matrix)
        for __ in range(n*n):
            neigh = getHCNeighbourhood(bestSol)
            # print(neigh)
            for j in range(len(neigh)):
                curOrder = neigh[j][0]
                curEnc = neigh[j][1]
                # print(curEnc, curOrder)
                curFit = getFitnessOfSolution((curOrder,curEnc), matrix)
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

#TODO: implementirati GA sljedece
# 1) Ne znam jel se isplati napraviti HC kod odabira početne generacije za GA
# 2) Treba odlučiti koja vrsta GA je bolja ili kako cemo tocno
def selectionForGA(neigh: np.array, matrix: np.array):
    pass

def crossingForGA():
    pass

# Ovdje upisujemo parametre
# n -> veličina matrice
# cut -> koliko dobra mora biti šansa za uspijeh transplatacije da bi je obavili
n = 30
matrix = getMatrix(n)
cut = 0.5
matrix01 = get01Matrix(matrix, cut)

# fitDrawn = getFitnessOfDrawnSolution(getDrawnSolution(sol), matrix01)
# print(fitDrawn)

bestSol, bestFit = hillClimbing(n, 5, matrix01)
print(bestFit)
print(getDrawnSolution(bestSol))
# print(getDrawnSolution(sol))