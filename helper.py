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

def getEnclousure(numOfPairs: int):
    enc = []
    sum = 0
    while sum < numOfPairs:
        [t] = np.random.randint(1, 4, 1)
        sum += t
        if sum > numOfPairs:
            t = t - (sum - numOfPairs)
            if t <= 0:
                break
        enc.append(t)
    return enc

# 1) Mislim da je ovo najfleksibilniji prikaz rješenja, zauzima duplo memorije, ali memorija nije probelm
def getRandomStartingSolution(numOfPairs: int):
    order = np.random.permutation(numOfPairs)
    enc = getEnclousure(numOfPairs)
    return (order, enc)

# 1) Za svaki ciklus gleda je li svi u ciklusu imaju transplataciju i onda je fit += len(ciklusa)
def getFitnessOfSolution(sol: tuple, matrix):
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
    # print(fit)
    return fit

# 1) Vraća nacrtano rješenje koje sadrži samo ntuplove čije će se operacije dogoditi  
def getFinalDrawnSolution(sol: tuple, matrix):
    order, enc = sol
    order = order.tolist()
    cur = 0
    j = 0
    while j < len(enc):
        l = enc[j] #prolazimo po enc listi
        ntup = order[cur : cur + l]
        i = 0
        ntupWorks = True
        while i < l: #prolazimo po dijelu order liste duljine l
            a = ntup[i]
            b = None
            if i == l - 1:
                b = ntup[0]
            else:
                b = ntup[i + 1]
            if matrix[a][b] == 0: #ako trenutni ciklus (lanac) nije dobar, brišemo ga
                del enc[j]  #brišemo iz enc liste element koji ne cini dobar ciklus (lanac)
                for k in range(l): #brišemo iz order liste id-eve koji ne cien dobar ciklus (lanac)
                    del order[cur]
                ntupWorks = False
                break
            i += 1
        if ntupWorks:
            cur += l
            j += 1
    return getDrawnSolution((order, enc))

def swap(lista, i: int, j: int):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp
        return lista

# 1) Jedan enc se smanji ako je veci od 1, a jedan se poveca ako je manji od 3
def changeEnc(enc, i: int, j: int):
    a = enc[i]
    b = enc[j]
    if a != 1 and b != 3:
        enc[i] = a - 1
        enc[j] = b + 1
    elif a != 3 and b != 1:
        enc[i] = a + 1
        enc[j] = b - 1
    return enc
