import sys
import hc
import ga
import helper
import numpy as np
from timeit import default_timer as timer

args = sys.argv

fileName = args[1]
json = args[2]
alg = args[3]
numOfIter = int(args[4])
popSize = int(args[5])
selectionSize = int(args[6])
orderMutateProb = float(args[7])
encMutateProb = float(args[8])
selectionMode = args[9]

# fileName = "genjson-100.json"
# json = "True"
# alg = "hc"
# numOfIter = 10
# popSize = 4000
# selectionSize = 1000
# orderMutateProb = 0.01
# encMutateProb = 0.05
# selectionMode = "top"

#rječnik koji služi za ispravno vraćanje id-eva u slučaju da izbacimo redak i stupac koji imaju samo nule
transformDict = matrix = None
#različito parsiranje ovisno o ulaznim podacima
if json == "True":
    transformDict, matrix = helper.getJsonMatrix(fileName)
else:
    transformDict, matrix = helper.getMatrix(fileName)

fit = None
sol = [0,0,0]
numOfPairs = len(matrix)
matrix = np.array(matrix, dtype=np.int32)

start = timer()
if alg == "ga":
    sol[0], sol[1], sol[2], fit = ga.geneticAlgorithm(popSize, numOfPairs, selectionSize, encMutateProb,
                                                      orderMutateProb, numOfIter, matrix, selectionMode)
elif alg == "hc":
    sol[0], sol[1], sol[2], fit = hc.hillClimbing(numOfPairs, numOfIter, matrix)
end = timer()
print("Vrijeme izvršavanja algoritma: ", end - start, " sekundi.")

if sol == None:
    print("Ne postoji niti jedna moguća transplatacija.")

drawnSol = helper.getFinalDrawnSolution(sol, matrix)
for ntup in drawnSol:
    for i in range(len(ntup)):
        ntup[i] = transformDict[ntup[i]]

print("Broj transplatacija: ", fit)
print("Prikaz transplatacija: ", drawnSol)