import numpy as np
from numba import njit
import numba as nb
import json

# 1) Ova funkcija služi samo radi ljepšeg prikaza rješenja
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

@njit
def getEnclousure(numOfPairs: int):
    enc = np.empty(numOfPairs, dtype=np.short)
    sum = 0
    i = 0
    while sum < numOfPairs:
        to = min(4,numOfPairs-sum + 1)
        [t] = np.random.randint(1, to , 1)
        sum += t
        enc[i] = t
        i += 1
    return enc, i

@njit
def getRandomStartingSolution(numOfPairs: int) -> tuple:
    order = np.random.permutation(numOfPairs)
    enc, size = getEnclousure(numOfPairs)
    return order, enc, size

# 1) Za svaki ciklus gleda je li svi u ciklusu imaju transplataciju i onda je fit += len(ciklusa)
@njit
def getFitnessOfSolution(sol: tuple, matrix):
    order, enc, encLen = sol
    fit = 0
    cur = 0
    for j in range(encLen):
        l = enc[j]
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

# 1) Vraća nacrtano rješenje koje sadrži samo ntuplove čije će se operacije dogoditi  
def getFinalDrawnSolution(sol: tuple, matrix):
    sol = getDrawnSolution(sol)
    n = len(sol)
    i = 0
    while i < n:
        ntup = sol[i]
        m = len(ntup)
        for j in range(m):
            a = ntup[j]
            b = None
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

@njit((nb.int16[:], nb.int16, nb.int16))
def swap(lista, i: int, j: int):
        temp = lista[i]
        lista[i] = lista[j]
        lista[j] = temp
        return

# 1) Mijenjaju se po pravilu tako da omjer svih ostane isti nakon mutacije da se spriječi
# konvergiranje prema jednom broju
        # 1-1 -> 0-2
        # 1-2 -> 0-3
        # 1-3 -> 2-2
        # 2-1 -> 1-2
        # 2-2 -> 1-3
        # 2-3 -> 1-3-1
        # 3-1 -> 1-3
        # 3-2 -> 2-3
        # 3-3 -> 2-3-1
@njit(nb.int16(nb.int16[:], nb.int16, nb.int16, nb.int16))
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
    if enc[i] == 0:
        for k in range(i, encLen):
            enc[k] = enc[k + 1]
        encLen -= 1
    return encLen

def getNumber(id, curNum, dict):
    if id not in dict:
        dict[id] = curNum
        curNum += 1
    return dict[id], curNum

def getJsonMatrix(fileName):
    matrixDim = 0
    dict = {}
    curNum = 0
    matrixDict = {}
    with open(fileName) as f:
        data = json.loads(f.read())["data"]
    for key in data:
        if int(key) > matrixDim:
            matrixDim = int(key)
        matrixKey, curNum = getNumber(int(key), curNum, dict)
        matrixDict[matrixKey] = []
        for match in data[key]["matches"]:
            recipientId = match["recipient"]
            if recipientId > matrixDim:
                matrixDim = recipientId
            matrixRecipient, curNum = getNumber(recipientId, curNum, dict)
            matrixDict[matrixKey].append(matrixRecipient)

    n = len(dict)
    matrix = np.zeros((n,n), dtype=np.short)
    for recipientId in matrixDict:
        for donorId in matrixDict[recipientId]:
            matrix[donorId][recipientId] = 1
    inverseDict = {v: k for k, v in dict.items()}
    return inverseDict, matrix

def getMatrix(fileName: str):
    matrix = []
    toDel = []
    
    with open(fileName) as f:
        lines = f.readlines()
        i = 0
        for line in lines:
            line = line[:-2]
            arr = [int(numOfPairs) for numOfPairs in line.split(",")]
            matrix.append(arr)
            if all(v == 0 for v in arr):
                toDel.append(i)
            i += 1
    n = len(matrix)
    transformDict = {}
    transformList = filter(lambda x: x not in toDel, list(range(n)))
    for i in transformList:
        transformDict[i] = i
        
    for i in reversed(toDel):
        del matrix[i]
        for k,v in transformDict.items():
            if k > i:
                transformDict[k] = v - 1
        n = len(matrix)
        for j in range(n):
            del matrix[j][i]

    inverseDict = {v: k for k, v in transformDict.items()}
    return inverseDict, np.array(matrix, dtype=np.short)