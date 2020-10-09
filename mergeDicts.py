import json
import xlsxwriter

with open("data/old/results.json") as json_file:
    dataOne = json.load(json_file)

with open("data/results.json") as json_file:
    dataTwo = json.load(json_file)

with open("data/old/cycleData.json") as json_file:
    cycleOne = json.load(json_file)

with open("data/cycleData.json") as json_file:
    cycleTwo = json.load(json_file)


mergedCycle = {}

for key in cycleOne:
    mergedCycle[key] = cycleOne[key]

for keyTwo in cycleTwo:
    mergedCycle[str(int(key)+int(keyTwo))] = cycleTwo[keyTwo]

z = {**dataOne, **dataTwo}

with open('data/mergedRes.json', 'w') as fp:
    json.dump(z, fp)

with open('data/mergedCycle.json', 'w') as fp:
    json.dump(mergedCycle, fp)

test = 2
