import sys
import hc
import ga
import helper
import numpy as np

# args = sys.argv

# fileName = args[1]
# json = args[2]
# alg = args[3]
# numOfIter = int(args[4])
# popSize = int(args[5])
# selectionSize = int(args[6])
# orderMutateProb = float(args[7])
# encMutateProb = float(args[8])
# selectionMode = args[9]

fileName = "genjson-100.json"
json = "True"
alg = "ga"
numOfIter = 4000
popSize = 1000
selectionSize = 200
orderMutateProb = 0.01
encMutateProb = 0.05
selectionMode = "top"

transformDict = matrix = None
if json == "True":
    transformDict, matrix = helper.getJsonMatrix(fileName)
else:
    transformDict, matrix = helper.getMatrix(fileName)

fit = None
sol = [0,0,0]
numOfPairs = len(matrix)
matrix = np.array(matrix, dtype=np.short)
if alg == "ga":
    sol[0], sol[1], sol[2], fit = ga.geneticAlgorithm(popSize, numOfPairs, selectionSize, encMutateProb, orderMutateProb, numOfIter, matrix, selectionMode)
elif alg == "hc":
    sol, fit = hc.hillClimbing(numOfPairs, numOfIter, matrix)

drawnSol = helper.getFinalDrawnSolution(sol, matrix)
for ntup in drawnSol:
    for i in range(len(ntup)):
        ntup[i] = transformDict[ntup[i]]

print("Dobiveni fit: ", fit)
# print("Dobiveno rješenje: ", sol[0])
# print(sol[1][:sol[2]])

print(drawnSol)