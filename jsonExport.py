import json
import matplotlib.pyplot as plt
import csv
import sys

with open("data/results.json") as json_file:
    data = json.load(json_file)

with open("data/cycleData.json") as json_file:
    cycledata = json.load(json_file)

graph = {}

for i in data:
    if data[i]['miner']['node'] not in graph:
        graph[data[i]['miner']['node']] = {}
        graph[data[i]['miner']['node']]['startBalance'] = data[i]['miner']['balanceBefore']
        graph[data[i]['miner']['node']]['x'] = []
        graph[data[i]['miner']['node']]['y'] = []
        graph[data[i]['miner']['node']]['diff'] = []
        graph[data[i]['miner']['node']]['offset'] = 0.0


    graph[data[i]['miner']['node']]['x'].append(int(i))
    result = data[i]['miner']['balanceNow']-graph[data[i]['miner']['node']]['startBalance']+graph[data[i]['miner']['node']]['offset']
    if result < 0.0:
        graph[data[i]['miner']['node']]['offset'] = graph[data[i]['miner']['node']]['offset'] - result + graph[data[i]['miner']['node']]['y'][-1]

        result = data[i]['miner']['balanceNow']-graph[data[i]['miner']['node']]['startBalance']+graph[data[i]['miner']['node']]['offset']

    graph[data[i]['miner']['node']]['y'].append(result)
    graph[data[i]['miner']['node']]['diff'].append(data[i]['miner']['diff'])

    for dele in data[i]['delegator']:
        delegatorStr = dele+'-delegate'
        if delegatorStr not in graph:
            graph[delegatorStr] = {}
            graph[delegatorStr]['startBalance'] = data[i]['delegator'][dele]['balanceBefore']
            graph[delegatorStr]['x'] = []
            graph[delegatorStr]['y'] = []
            graph[delegatorStr]['diff'] = []
            graph[delegatorStr]['offset'] = 0.0
        graph[delegatorStr]['x'].append(int(i))
        result = data[i]['delegator'][dele]['balanceNow'] - graph[delegatorStr]['startBalance'] + graph[delegatorStr]['offset']
        if result < 0.0:
            graph[delegatorStr]['offset'] = graph[delegatorStr]['offset'] - result + graph[delegatorStr]['y'][-1]

            result = data[i]['delegator'][dele]['balanceNow'] - graph[delegatorStr]['startBalance'] + graph[delegatorStr]['offset']
        graph[delegatorStr]['y'].append(result)
        graph[delegatorStr]['diff'].append(data[i]['delegator'][dele]['diff'])

lowestX = sys.maxsize
highestX = 0

for key in graph:
    plt.plot(graph[key]['x'], graph[key]['y'], label=key)
    if graph[key]['x'][0] < lowestX:
        lowestX = graph[key]['x'][0]
    if graph[key]['x'][-1] > highestX:
        highestX = graph[key]['x'][-1]

plt.legend()
plt.show()

fig = plt.figure()
ax1 = fig.add_subplot(111)

for key in graph:
    ax1.scatter(graph[key]['x'],graph[key]['diff'],s=1, label=key)


plt.xlim(left=lowestX)
plt.xlim(right=highestX)
plt.ylim(bottom=0)
plt.ylim(top=5)
plt.legend()
plt.show()


cycleGraph = {}
pieChart = {}


for i in cycledata:
    plt.plot(x=cycledata[i]['startBlock'], color='gray')
    for subCycle in cycledata[i]['subCycleData']:
        for val in cycledata[i]['subCycleData'][subCycle]['validators']:
            if type(cycledata[i]['subCycleData'][subCycle]['validators'][val]) is dict:
                if val not in cycleGraph:
                    cycleGraph[val] = {}
                    cycleGraph[val]['x'] = []
                    cycleGraph[val]['y'] = []
                cycleGraph[val]['x'].append(cycledata[i]['subCycleData'][subCycle]['startBlock'])
                cycleGraph[val]['y'].append(cycledata[i]['subCycleData'][subCycle]['validators'][val]['rewardPerBlock'])
                cycleGraph[val]['x'].append(cycledata[i]['subCycleData'][subCycle]['endBlock'])
                cycleGraph[val]['y'].append(cycledata[i]['subCycleData'][subCycle]['validators'][val]['rewardPerBlock'])

for key in cycleGraph:
    plt.plot(cycleGraph[key]['x'], cycleGraph[key]['y'], label=key)

plt.legend()
plt.show()