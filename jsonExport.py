import json
import matplotlib.pyplot as plt
import csv

with open("data/results.json") as json_file:
    data = json.load(json_file)

with open("data/cycleData.json") as json_file:
    cycledata = json.load(json_file)

# AP This is to fix a bug in the main testnet code will find it later!
# for i in cycledata:
#     lastKey = list(cycledata[i]['subCycleData'])[-1]
#     for subCycle in cycledata[i]['subCycleData']:
#         if subCycle == lastKey:
#             cycledata[i]['subCycleData'][subCycle]['endBlock'] = cycledata[i]['endBlock']
#         else:
#             cycledata[i]['subCycleData'][subCycle]['endBlock'] = cycledata[str(int(i)+1)]['startBlock'] - 1
#
#
# with open('data/cycleData.csv', 'w') as f:
#     w = csv.writer(f)
#     w.writerows(cycledata.items())
#     print('Done writing cycleData.csv')
#
# with open('data/cycleData.json', 'w') as fp:
#     json.dump(cycledata, fp)
#     print('Done writing cycleData.json')

graph = {}

for i in data:
    if data[i]['miner']['node'] not in graph:
        graph[data[i]['miner']['node']] = {}
        graph[data[i]['miner']['node']]['startBalance'] = data[i]['miner']['balanceBefore']
        graph[data[i]['miner']['node']]['x'] = []
        graph[data[i]['miner']['node']]['y'] = []
        graph[data[i]['miner']['node']]['offset'] = 0.0


    graph[data[i]['miner']['node']]['x'].append(int(i))
    result = data[i]['miner']['balanceNow']-graph[data[i]['miner']['node']]['startBalance']+graph[data[i]['miner']['node']]['offset']
    if result < 0.0:
        graph[data[i]['miner']['node']]['offset'] = graph[data[i]['miner']['node']]['offset'] - result + graph[data[i]['miner']['node']]['y'][-1]

        result = data[i]['miner']['balanceNow']-graph[data[i]['miner']['node']]['startBalance']+graph[data[i]['miner']['node']]['offset']

    graph[data[i]['miner']['node']]['y'].append(result)

    for dele in data[i]['delegator']:
        delegatorStr = dele+'-delegate'
        if delegatorStr not in graph:
            graph[delegatorStr] = {}
            graph[delegatorStr]['startBalance'] = data[i]['delegator'][dele]['balanceBefore']
            graph[delegatorStr]['x'] = []
            graph[delegatorStr]['y'] = []
            graph[delegatorStr]['offset'] = 0.0
        graph[delegatorStr]['x'].append(int(i))
        result = data[i]['delegator'][dele]['balanceNow'] - graph[delegatorStr]['startBalance'] + graph[delegatorStr]['offset']
        if result < 0.0:
            graph[delegatorStr]['offset'] = graph[delegatorStr]['offset'] - result + graph[delegatorStr]['y'][-1]

            result = data[i]['delegator'][dele]['balanceNow'] - graph[delegatorStr]['startBalance'] + graph[delegatorStr]['offset']
        graph[delegatorStr]['y'].append(result)


for key in graph:
    plt.plot(graph[key]['x'], graph[key]['y'], label=key)

plt.legend()
plt.show()

cycleGraph = {}
pieChart = {}


for i in cycledata:
    pieChart[i] = {}
    pieChart[i]['nodeName'] = []
    pieChart[i]['nodeShare'] = []
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
#                 pieChart[i]['nodeName'].append(val)
#                 pieChart[i]['nodeShare'].append(cycledata[i][val]['rewardToNode'])
#                 pieChart[i]['title'] = "cycle " + str(cycledata[i]['startBlock']) + " to " + str(cycledata[i]['endBlock']) + " ( " + str(cycledata[i]['cycleLength']) + " blocks )"
#
# # skip first X pie charts
# skipPieCharts = 80
# for key in pieChart:
#     if (int(key) > skipPieCharts):
#         plt.pie(pieChart[key]['nodeShare'], labels=pieChart[key]['nodeName'],
#             autopct='%1.1f%%', startangle=140)
#
#         plt.title(pieChart[key]['title'])
#         plt.axis('equal')
#         plt.savefig('pieCharts/'+ pieChart[key]['title'] + '.jpeg', dpi=300, bbox_inches='tight')
#         plt.clf()

for key in cycleGraph:
    plt.plot(cycleGraph[key]['x'], cycleGraph[key]['y'], label=key)

plt.legend()
plt.show()