import json
import matplotlib.pyplot as plt
import csv
import sys

with open("data/results.json") as json_file:
    data = json.load(json_file)

with open("data/cycleData.json") as json_file:
    cycledata = json.load(json_file)

test = 1

with open( "data/results.csv", "w") as csv_file:
    csv_file.write("block,node,balanceBefore,balanceNow,diff,expectedReward,transFees,Delegate,balanceBefore,balanceNow,diff,expectedReward\n")

    for key in data:
        line = str(key) + ','
        for valKey in data[key]['miner']:
            line += str(data[key]['miner'][valKey]) + ','



        for delegate in data[key]['delegator']:
            line += delegate + ','
            for delkey in data[key]['delegator'][delegate]:
                line += str(data[key]['delegator'][delegate][delkey]) + ','

        line = line[:-1]

        csv_file.write(line+'\n')