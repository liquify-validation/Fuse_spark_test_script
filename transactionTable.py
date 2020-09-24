__author__ = 'Andy Pohl'
__maintainer__ = 'Andy Pohl'
__email__ = 'andy@liquify-validation.com'
__date__ = '2020/09/24'
__description__ = 'Script to generate a transaction data table for all inbound and outbound transaction of validators and delegates. (used for network testing)'

from web3 import Web3
import csv
import json

RPC_ADDRESS = 'https://testrpc.fuse.io/'
web3Fuse = Web3(Web3.HTTPProvider(RPC_ADDRESS))

#build a table of all the validators and delegators active across the test
def buildTransactionDict(transTable,cycleData):
    transTable['validators'] = {}
    transTable['delegators'] = {}
    for cycle in cycleData:
        for subCycle in cycleData[cycle]['subCycleData']:
            for val in cycleData[cycle]['subCycleData'][subCycle]['validators']:
                if val not in transTable['validators']:
                    transTable['validators'][val] = {}
                    transTable['validators'][val]['to'] = {}
                    transTable['validators'][val]['from'] = {}
                for delegate in cycleData[cycle]['subCycleData'][subCycle]['validators'][val]['delegators']:
                    if delegate not in transTable['delegators']:
                        transTable['delegators'][delegate] = {}
                        transTable['delegators'][delegate]['to'] = {}
                        transTable['delegators'][delegate]['from'] = {}



with open("data/cycleData.json") as json_file:
    cycledata = json.load(json_file)

transactionDict = {}

buildTransactionDict(transactionDict,cycledata)

#get the start and end block from the cycledata (generated by running testnet.py)
startCycle = cycledata['0']['startBlock']
endCycle = cycledata[list(cycledata)[-1]]['endBlock']

#loop across blocks and check for transactions
for i in range (startCycle, endCycle, 1):
    block = web3Fuse.eth.getBlock(i)
    miner = block['miner']
    trans = block['transactions']

    #loop across transactions and check if any are to/from a validator/delegate if they are then add it to the data table
    for tran in trans:
        transaction = web3Fuse.eth.getTransaction(tran)

        if transaction['to'] in transactionDict['validators']:
            if i not in transactionDict['validators'][transaction['to']]['to']:
                transactionDict['validators'][transaction['to']]['to'][i] = {}
                transactionDict['validators'][transaction['to']]['to'][i]['transCount'] = 1
            else:
                transactionDict['validators'][transaction['to']]['to'][i]['transCount'] += 1
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']] = {}
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['hash'] = web3Fuse.toHex(transaction['hash'])
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['from'] = transaction['from']
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['value'] = transaction['value']/10**18
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['gas'] = transaction['gas']
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['gasPrice'] = transaction['gasPrice']
            transactionDict['validators'][transaction['to']]['to'][i][transactionDict['validators'][transaction['to']]['to'][i]['transCount']]['transFee'] = (transaction['gas'] * transaction['gasPrice'])/10**18
        elif transaction['to'] in transactionDict['delegators']:
            if i not in transactionDict['delegators'][transaction['to']]['to']:
                transactionDict['delegators'][transaction['to']]['to'][i] = {}
                transactionDict['delegators'][transaction['to']]['to'][i]['transCount'] = 1
            else:
                transactionDict['delegators'][transaction['to']]['to'][i]['transCount'] += 1
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']] = {}
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['hash'] = web3Fuse.toHex(transaction['hash'])
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['from'] = transaction['from']
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['value'] = transaction['value']/10**18
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['gas'] = transaction['gas']
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['gasPrice'] = transaction['gasPrice']
            transactionDict['delegators'][transaction['to']]['to'][i][transactionDict['delegators'][transaction['to']]['to'][i]['transCount']]['transFee'] = (transaction['gas'] * transaction['gasPrice'])/10**18
        elif transaction['from'] in transactionDict['validators']:
            if i not in transactionDict['validators'][transaction['from']]['from']:
                transactionDict['validators'][transaction['from']]['from'][i] = {}
                transactionDict['validators'][transaction['from']]['from'][i]['transCount'] = 1
            else:
                transactionDict['validators'][transaction['from']]['from'][i]['transCount'] += 1
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']] = {}
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['hash'] = web3Fuse.toHex(transaction['hash'])
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['from'] = transaction['to']
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['value'] = transaction['value'] / 10 ** 18
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['gas'] = transaction['gas']
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['gasPrice'] = transaction['gasPrice']
            transactionDict['validators'][transaction['from']]['from'][i][transactionDict['validators'][transaction['from']]['from'][i]['transCount']]['transFee'] = (transaction['gas'] * transaction['gasPrice']) / 10 ** 18
        elif transaction['from'] in transactionDict['delegators']:
            if i not in transactionDict['delegators'][transaction['from']]['from']:
                transactionDict['delegators'][transaction['from']]['from'][i] = {}
                transactionDict['delegators'][transaction['from']]['from'][i]['transCount'] = 1
            else:
                transactionDict['delegators'][transaction['from']]['from'][i]['transCount'] += 1
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']] = {}
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['hash'] = web3Fuse.toHex(transaction['hash'])
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['from'] = transaction['to']
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['value'] = transaction['value'] / 10 ** 18
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['gas'] = transaction['gas']
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['gasPrice'] = transaction['gasPrice']
            transactionDict['delegators'][transaction['from']]['from'][i][transactionDict['delegators'][transaction['from']]['from'][i]['transCount']]['transFee'] = (transaction['gas'] * transaction['gasPrice']) / 10 ** 18

    if i % 250 == 0:
        print("atBlock ", str(i))

    if i % 5000 == 0:
        with open('data/transactionData.json', 'w') as fp:
            json.dump(transactionDict, fp)


with open('data/transactionData.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(transactionDict.items())
    print('Done writing transactionData.csv')

with open('data/transactionData.json', 'w') as fp:
    json.dump(transactionDict, fp)
    print('Done writing transactionData.json')