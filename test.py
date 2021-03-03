import numpy as np
import helper
import ga 

def getTestMatrix(numOfPairs: int, fit: int):
    matrix = np.full((numOfPairs,numOfPairs), 0)
    enc = helper.getEnclosure(numOfPairs)
    rng = np.random.default_rng()
    idList = rng.choice(numOfPairs, fit, replace=False)
    cur = 0
    for l in enc:
        for i in range(l):
            a = idList[cur + i]
            b = None
            if i == l - 1:
                b = idList[cur]
            else:
                b = idList[cur + i + 1]
            matrix[a][b] = 1
        cur += l
    return (matrix, (idList, enc))

numOfPairs = 10