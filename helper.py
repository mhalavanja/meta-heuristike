import numpy as np
from numba import njit
import numba as nb
import json

#funkcija služi samo radi ljepšeg prikaza rješenja
def getDrawnSolution(sol: tuple):
    order, enc, encLen = sol
    ret = []
    cur = 0
    i = 0
    for i in range(encLen):
        ntup = enc[i]
        tup = [order[cur + i] for i in range(ntup)]
        ret.append(tup)
        cur += ntup
    return ret

#vrati nasumičnu listu enclosure
@njit
def getEnclosure(numOfPairs: int):
    enc = np.empty(numOfPairs, dtype=np.int32)
    sum = 0
    i = 0
    while sum < numOfPairs:
        to = min(4,numOfPairs-sum + 1)
        [t] = np.random.randint(1, to , 1)
        sum += t
        enc[i] = t
        i += 1
    return enc, i

#za svaki ciklus gleda je li svi u ciklusu imaju transplataciju i onda je fit += len(ciklusa)
@njit
def getFitnessOfSolution(sol: tuple, matrix):
    order, enc, encLen = sol
    fit = 0
    cur = 0
    for j in range(encLen): #prolazimo po duljini enclosure liste
        l = enc[j]  #trenutni enc
        ntup = order[cur : cur + l] #1,2 ili 3 ciklus za koji žeelimo odrediti je li uspješan ili ne
        ntupWorks = True #pretpostavimo da je trenutni ciklus uspješan
        for i in range(l):
            a = ntup[i]
            if i == l - 1:
                b = ntup[0] #ako je a zadnji element u ciklusu, b je prvi
            else:
                b = ntup[i + 1] #inače je b sljedeći element nakon a u ciklusu
            if matrix[a][b] == 0:
                ntupWorks = False
                break
        if ntupWorks:
            fit += l
        cur += l #preskačemo elemente koje smo provjerili u trenutnom ciklusu
    return fit

#vraća nacrtano rješenje koje sadrži samo ntuplove čije će se operacije dogoditi
def getFinalDrawnSolution(sol: tuple, matrix):
    sol = getDrawnSolution(sol)
    n = len(sol)
    i = 0
    while i < n:
        ntup = sol[i]
        m = len(ntup)
        for j in range(m):
            a = ntup[j]
            if j == m - 1:
                b = ntup[0]
            else:
                b = ntup[j + 1]
            if matrix[a][b] == 0:  # ako trenutni ciklus nije dobar, brišemo ga
                del sol[i]
                i -= 1
                n -= 1
                break
        i += 1
    return sol

@njit((nb.int32[:], nb.int32, nb.int32))
def swap(lista, i: int, j: int):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp

#mijenjaju se po pravilu tako da omjer svih ostane isti nakon mutacije da se spriječi
# konvergiranje t.d. neki broj nestane
        # 1-1 -> 0-2
        # 1-2 -> 0-3
        # 1-3 -> 2-2
        # 2-1 -> 1-2
        # 2-2 -> 1-3
        # 2-3 -> 1-3-1
        # 3-1 -> 1-3
        # 3-2 -> 2-3
        # 3-3 -> 2-3-1
@njit(nb.int32(nb.int32[:], nb.int32, nb.int32, nb.int32))
def changeEnc(enc, encLen, i: int, j: int):
    a = enc[i]
    b = enc[j]
    if a == 1 and b == 3:
        enc[i] = 2
        enc[j] = 2
    elif a == 2 and b == 3:
        enc[i] = 1
        enc[encLen] = 1
        encLen += 1
    elif a == 3 and b == 1:
        enc[i] = 1
        enc[j] = 3
    elif a == 3 and b == 3:
        enc[i] = 2
        enc[encLen] = 1
        encLen += 1
    else:
        enc[i] = a - 1
        enc[j] = b + 1
    if enc[i] == 0: #mičemo elemente koji su jednaki 0 iz enclosure liste i pomičemo sve iza njega unaprijed
        for k in range(i, encLen):
            enc[k] = enc[k + 1]
        encLen -= 1
    return encLen

#funkcija za mapiranje id-eva kod parsiranja
def getNumber(id, curNum, dict):
    if id not in dict:
        dict[id] = curNum
        curNum += 1
    return dict[id], curNum

#funkcija za parsiranje json datoteke
def getJsonMatrix(fileName):
    matrixDim = 0
    dict = {}
    curNum = 0
    matrixDict = {} #id-evi u json datoteci nisu brojevi koji idu redom pa ih moramo znati mapirati

    with open(fileName) as f:
        data = json.loads(f.read())["data"]
    for key in data:
        if int(key) > matrixDim:
            matrixDim = int(key)
        matrixKey, curNum = getNumber(int(key), curNum, dict)
        matrixDict[matrixKey] = []


        if "matches" not in data[key].keys(): #ako dani donor nema nijednog mogućeg primatelja
            continue
        #struktura json datoteke je takva da za danog donora su pobrojani njegovi potencijalni primatelji
        for match in data[key]["matches"]:
            recipientId = match["recipient"]
            if recipientId > matrixDim:
                matrixDim = recipientId
            matrixRecipient, curNum = getNumber(recipientId, curNum, dict) #proces mapiranja id-eva
            matrixDict[matrixKey].append(matrixRecipient)

    n = len(dict)
    matrix = np.zeros((n,n), dtype=np.int32)
    for recipientId in matrixDict:
        for donorId in matrixDict[recipientId]:
            matrix[recipientId][donorId] = 1
    inverseDict = {v: k for k, v in dict.items()} #obrnuti rječnik za mapiranje id-eva kada nakon algoritma
    return inverseDict, matrix

#funkcija za parsiranje nejson datoteke
def getMatrix(fileName: str):
    matrix = []
    toDel = [] #retke koji imaju samo nule za elemente možemo obrisati, kao i pripadne stupce
    
    with open(fileName) as f:
        lines = f.readlines()
        i = 0
        for line in lines:
            line = line[:-2]
            arr = [int(numOfPairs) for numOfPairs in line.split(",")]
            matrix.append(arr)
            if all(v == 0 for v in arr):
                toDel.append(i) #sve nule, označavamo ga za brisanje
            i += 1

    n = len(matrix)
    transformDict = {}
    transformList = filter(lambda x: x not in toDel, list(range(n)))
    for i in transformList:
        transformDict[i] = i

    #kada obrišemo retke i stupce koji su samo nule, moramo znati mapirati preostale id-eve u početne
    for i in reversed(toDel):
        del matrix[i]
        for k,v in transformDict.items():
            if k > i:
                transformDict[k] = v - 1
        n = len(matrix)
        for j in range(n):
            del matrix[j][i]

    inverseDict = {v: k for k, v in transformDict.items()}
    return inverseDict, np.array(matrix, dtype=np.int32)