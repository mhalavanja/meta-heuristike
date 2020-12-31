import numpy as np
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

# 1) Koliko treba biti susjedstvo?
# 2) Susjedstvo mozemo mijenjati takoder da mijenjamo i granice mozda
# 3) Mislim da je bolje kada mijenjamo i granice
def getHCNeighbourhood(sol: tuple):
    order, enc = sol
    neigh = []
    swapPairs = np.random.randint(0, n, 2 * n)
    changeWhat = np.random.randint(0, 2, n)
    encToChange = np.random.randint(0, len(enc), 2 * n)
    for i in range(n):
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
            for j in range(len(neigh)):
                curOrder = neigh[j][0]
                curEnc = neigh[j][1]
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
def selectionForGA(generation: np.array, line: np.array, fitSum: int, k: int):
    selected = []
    p = fitSum/float(k)
    [r] = np.random.uniform(0, p, 1)
    cur = 0
    for i in range (k):
        curPointer = r + float(i * p)
        while curPointer - line[cur][0] < 0:
            cur += 1
        selected.append(generation[cur])
    return selected

def mutate(sol: tuple):
    order, enc = sol
    swapPairs = np.random.randint(0, n, 2)
    [changeWhat] = np.random.randint(0, 2, 1)
    encToChange = np.random.randint(0, len(enc), 2)
    if changeWhat == 0 or encToChange[0] == encToChange[1]:
        return(swap(order, swapPairs[0], swapPairs[1]), enc)
    else:
        return(order, changeEnc(enc, encToChange[0], encToChange[1]))

# 1) Koristimo križanje poretka zato što je bitan redosljed u kojem su brojevi, a ne 
#    njihov apsolutni poredak u listi
def crossingForGA(n: int, k: int, population: np.array):
    def crossing(n: int, solA: tuple, solB: tuple):
        [pos1, pos2] = np.random.randint(0, n, 2)
        if pos2 < pos1:
            tmp = pos1
            pos1 = pos2
            pos2 = tmp
        [orderA, encA] = solA
        [orderB, encB] = solB
        childAord = [None] * n 
        childBord = [None] * n
        setA = set()
        setB = set()
        for i in range(pos1, pos2):
            childAord[i] = orderA[i]
            setA.add(orderA[i])
            childBord[i] = orderB[i]
            setB.add(orderB[i])
        j = pos2
        for i in range(pos2, n):
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                j += 1
        for i in range(0, pos1):
            if j == n:
                j = 0
            if orderB[i] not in setA:
                childAord[j] = orderB[i]
                j += 1
        j = pos2
        for i in range(pos2, n):
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                j += 1
        for i in range(0, pos1):
            if j == n:
                j = 0
            if orderA[i] not in setB:
                childBord[j] = orderA[i]
                j += 1
        return ((childAord, encA), (childBord, encB))

    # [l, s] = np.random.randint(0, n, 2) # l -> duljina ntupa, s -> startni indeks
    mutation = np.random.choice(2, n, p=[0.95, 0.05])
    newGeneration = []
    # l = l % 3 + 1
    cur = 0
    while cur < n:
        for i in range(k):
            a = population[i] #jos [0] ako se i fit prenosi s populacijom
            b = population[(2 * i) % k]
            c, d = crossing(n, a, b)
            if mutation[cur] == 1:
                c = mutate(c)
            if cur == n:
                return newGeneration
            cur += 1
            newGeneration.append(c)
            if mutation[cur] == 1:
                d = mutate(d)
            cur += 1
            newGeneration.append(d)
            if cur == n:
                return newGeneration
    return newGeneration

# 1) k je veličina populacije za križanje
def geneticAlgorithm(n: int, k: int, numOfIter: int, matrix: np.array):
    generation = []
    fitSum = 0
    line = []
    bestFit = 0
    bestSol = None
    for __ in range(numOfIter):    
        if len(generation) == 0:
            for __ in range(n):
                sol = getRandomStartingSolution(n)
                fit = getFitnessOfSolution(sol, matrix)
                if fit > bestFit:
                    bestFit = fit
                    bestSol = sol
                newFitSum = fitSum + fit
                line.append((fitSum, newFitSum))
                fitSum = newFitSum
                generation.append(sol) #mozda mozemo ovaj fit iskoristit i za kasnije
            selected = selectionForGA(generation, line, fitSum, k)
            generation = crossingForGA(n, k, selected)
        else:
            for i in range(n):
                sol = generation[i]
                fit = getFitnessOfSolution(sol, matrix)
                if fit > bestFit:
                    bestFit = fit
                    bestSol = sol
                newFitSum = fitSum + fit
                fitSum = newFitSum
                line.append((fitSum, newFitSum))
                generation.append((sol, fit))
            selected = selectionForGA(generation, line, fitSum, k)
            generation = crossingForGA(n, k, selected)
    return (bestSol, bestFit)

# Ovdje upisujemo parametre
# n -> veličina matrice
# cut -> koliko dobra mora biti šansa za uspijeh transplatacije da bi je obavili
n = 30
matrix = getMatrix(n)
cut = 0.5
matrix01 = get01Matrix(matrix, cut)

# fitDrawn = getFitnessOfDrawnSolution(getDrawnSolution(sol), matrix01)

# bestSol, bestFit = hillClimbing(n, 5, matrix01)
k = 10
numOfIter = 20
[sol, fit] = geneticAlgorithm(n, k, numOfIter, matrix01)
print(getDrawnSolution(sol))
print(fit)