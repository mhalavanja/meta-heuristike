import sys
import hc
import ga
import helper

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
# alg = "ga"
# numOfIter = 2000
# popSize = 100
# selectionSize = 50
# orderMutateProb = 0.01
# encMutateProb = 0.05
# selectionMode = "top"

transformDict = matrix = None
if json == "True":
    transformDict, matrix = helper.getJsonMatrix(fileName)
else:
    transformDict, matrix = helper.getMatrix(fileName)

sol = fit = None
if alg == "ga":
    sol, fit = ga.geneticAlgorithm(popSize, len(matrix), selectionSize, encMutateProb, orderMutateProb, numOfIter, matrix, selectionMode)
elif alg == "hc":
    sol, fit = hc.hillClimbing(len(matrix), 5, matrix)

drawnSol = helper.getFinalDrawnSolution(sol, matrix)
for ntup in drawnSol:
    for i in range(len(ntup)):
        ntup[i] = transformDict[ntup[i]]

print("Dobiveni fit: ", fit)
print("Dobiveno rješenje: ", drawnSol)