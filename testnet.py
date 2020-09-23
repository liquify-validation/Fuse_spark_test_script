from web3 import Web3
import csv
import json
from testnetCon import *
import copy





RPC_ADDRESS = 'https://testrpc.fuse.io/'
CONSENSUS_ADDR = Web3.toChecksumAddress('0xF5C4782d61611e12CD9651355841716ea1801d5c')
REWARD_ADDR = Web3.toChecksumAddress('0x3b8C048DdEC04709125aF939360BDD619Ec6e9E3')
web3Fuse = Web3(Web3.HTTPProvider(RPC_ADDRESS))

fuseConsensusContract = web3Fuse.eth.contract(abi=CONTRACT_ABI, address=CONSENSUS_ADDR)
blockRewardContract = web3Fuse.eth.contract(abi=blockRewardCon, address=REWARD_ADDR)


newBlock = web3Fuse.eth.blockNumber
# newBlock = 101000


inflation = blockRewardContract.functions.getInflation().call()
blocksPerYear = blockRewardContract.functions.getBlocksPerYear().call()

def getVals(data, block):
    vals = fuseConsensusContract.functions.currentValidators().call(block_identifier=block)
    for val in vals:
        data[val] = {}

def calculateStakedAmount(data, block):
    #data = dict of val data
    for val in data:
        delegatorsForVal = fuseConsensusContract.functions.delegators(val).call(block_identifier=block)
        data[val]["delegators"] = {}
        sumOfDelegates = 0
        for dele in delegatorsForVal:
            data[val]["delegators"][dele] = {}
            delegatedAmount = float(
                fuseConsensusContract.functions.delegatedAmount(dele, val).call(block_identifier=block) / 10 ** 18)
            data[val]["delegators"][dele][
                'Amount'] = delegatedAmount
            sumOfDelegates += delegatedAmount

        stakedAmount = float(fuseConsensusContract.functions.stakeAmount(val).call(block_identifier=block) / 10 ** 18)
        data[val]['stakedAmount'] = stakedAmount
        data[val]['selfStaked'] = stakedAmount - sumOfDelegates
        data[val]['fee'] = float(
            fuseConsensusContract.functions.validatorFee(val).call(block_identifier=block) / 10 ** 18)

    totalStakedCycle = 0
    for val in data:
        totalStakedCycle += data[val]['stakedAmount']

    return totalStakedCycle

def calculateRewards(data, totalStaked):
    valCounter = len(data)
    for val in data:
        #calc rewards
        data[val]['rewardToNode'] = infPerCycle * (data[val]['stakedAmount']/totalStaked)
        delegatesRewards = 0
        for dele in data[val]["delegators"]:
            data[val]["delegators"][dele]['reward'] = data[val]['rewardToNode'] * (data[val]["delegators"][dele]['Amount'] / data[val]['stakedAmount']) * (1-data[val]['fee'])
            data[val]["delegators"][dele]['rewardPerBlock'] = round((data[val]["delegators"][dele]['reward']/cycleDuration) * valCounter,6)
            delegatesRewards += data[val]["delegators"][dele]['reward']
        data[val]['reward'] = data[val]['rewardToNode'] - delegatesRewards
        data[val]['rewardPerBlock'] = round((data[val]['reward']/cycleDuration) * valCounter,6)
        
def checkForChange(data, subCycleSwap, block):
    retVal = False
    tempBlockData = {}
    getVals(tempBlockData, block)
    totalStaked = calculateStakedAmount(tempBlockData, block)
    #validatorDict[cycleCounter]['subCycleData'][0]['totalStaked'] = totalStaked
    calculateRewards(tempBlockData, totalStaked)

    if tempBlockData != data[subCycleSwap]['validators']:
        print("stakes have changed!")
        subCycleSwap+=1
        data[subCycleSwap] = {}
        data[subCycleSwap]['validators'] = copy.deepcopy(tempBlockData)
        data[subCycleSwap]['totalStaked'] = totalStaked
        data[subCycleSwap]['startBlock'] = block
        data[subCycleSwap]['endBlock'] = copy.deepcopy(data[subCycleSwap-1]['endBlock'])
        data[subCycleSwap - 1]['endBlock'] = block - 1
        retVal = True
    return retVal

initSupply = 300000000


cycleCounter = 0

startBlock = 100000

validatorDict = {}
upToo = 0

i = startBlock
#get the validators per cycle
while i < newBlock:
    valCounter = 0
    validatorDict[cycleCounter] = {}
    cycleDuration = fuseConsensusContract.functions.getCycleDurationBlocks().call(block_identifier=i)
    infPerYear = initSupply * (inflation / 100)
    infPerCycle = (infPerYear / blocksPerYear) * cycleDuration

    validatorDict[cycleCounter]['subCycleData'] = {}
    validatorDict[cycleCounter]['subCycleData'][0] = {}
    validatorDict[cycleCounter]['subCycleData'][0]['validators'] = {}

    getVals(validatorDict[cycleCounter]['subCycleData'][0]['validators'],i + 20)
    totalStaked = calculateStakedAmount(validatorDict[cycleCounter]['subCycleData'][0]['validators'],i)
    validatorDict[cycleCounter]['subCycleData'][0]['totalStaked'] = totalStaked
    calculateRewards(validatorDict[cycleCounter]['subCycleData'][0]['validators'],totalStaked)

    #skew the start if we have had new or left validators
    itr = 0
    if(cycleCounter != 0):
        if (len(validatorDict[cycleCounter]['subCycleData'][0]['validators']) != (len(validatorDict[cycleCounter-1]['subCycleData'][0]['validators']))):
            #check at what block we change at
            NotChanged = True
            oldLen = len(fuseConsensusContract.functions.currentValidators().call(block_identifier=i-1))

            while True:
                if(len(fuseConsensusContract.functions.currentValidators().call(block_identifier=i+itr)) != oldLen):
                    break
                itr+=1

            validatorDict[cycleCounter-1]['endBlock'] = (i-1) + itr

    validatorDict[cycleCounter]['startBlock'] = i + itr
    validatorDict[cycleCounter]['endBlock'] = fuseConsensusContract.functions.getCurrentCycleEndBlock().call(
        block_identifier=i) - 1
    validatorDict[cycleCounter]['cycleLength'] = validatorDict[cycleCounter]['endBlock'] - validatorDict[cycleCounter]['startBlock']
    validatorDict[cycleCounter]['propagation'] = itr

    validatorDict[cycleCounter]['subCycleData'][0]['startBlock'] = i + itr
    validatorDict[cycleCounter]['subCycleData'][0]['endBlock'] = i + itr




    start = fuseConsensusContract.functions.getCurrentCycleStartBlock().call(block_identifier=i+itr)
    end = fuseConsensusContract.functions.getCurrentCycleStartBlock().call(block_identifier=i) + cycleDuration
    i = fuseConsensusContract.functions.getCurrentCycleEndBlock().call(block_identifier=i) + 1
    cycleCounter += 1
    upToo = i

upToo = newBlock

print('Done gathering the  cycle data')

with open('data/cycleData.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(validatorDict.items())
    print('Done writing cycleData.csv')

with open('data/cycleData.json', 'w') as fp:
    json.dump(validatorDict, fp)
    print('Done writing cycleData.json')


data = {}

cycleSwap = 0
subCycleSwap = 0

oldTimeStamp = 0



for i in range (startBlock, upToo, 1):

    block = web3Fuse.eth.getBlock(i)
    miner = block['miner']
    trans = block['transactions']

    feeFromTrans = 0

    for tran in trans:
        transaction = web3Fuse.eth.getTransaction(tran)

        feeFromTrans += transaction['gas'] * transaction['gasPrice']

    feeFromTrans = float(feeFromTrans / 10 ** 18)

    data[i] = {}
    data[i]['miner'] = {}
    data[i]['miner']['node'] = miner
    data[i]['miner']['balanceBefore'] = float(web3Fuse.eth.getBalance(miner,i-1)/10**18)
    data[i]['miner']['balanceNow'] = float(web3Fuse.eth.getBalance(miner, i)/10**18)
    diff = (data[i]['miner']['balanceNow']) - (data[i]['miner']['balanceBefore'])
    data[i]['miner']['diff'] = round(diff,6)
    data[i]['miner']['expectedReward'] = validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]['rewardPerBlock']
    data[i]['miner']['transFees'] = feeFromTrans
    data[i]['delegator'] = {}

    for dele in validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]["delegators"]:
        data[i]['delegator'][dele] = {}
        data[i]['delegator'][dele]['balanceBefore'] = float(web3Fuse.eth.getBalance(dele, i - 1) / 10 ** 18)
        data[i]['delegator'][dele]['balanceNow'] = float(web3Fuse.eth.getBalance(dele, i) / 10 ** 18)
        diff = (data[i]['delegator'][dele]['balanceNow']) - (data[i]['delegator'][dele]['balanceBefore'])
        data[i]['delegator'][dele]['diff'] = round(diff, 6)
        data[i]['delegator'][dele]['expectedReward'] = validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]["delegators"][dele]['rewardPerBlock']
        if data[i]['delegator'][dele]['diff'] != validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]["delegators"][dele]['rewardPerBlock']:
            print("reward at block " + str(i) + " for delegator " + dele + " is not correct! expected " + str(validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]["delegators"][dele]['rewardPerBlock']) + " got " + str(data[i]['delegator'][dele]['diff']))
            if(checkForChange(validatorDict[cycleSwap]['subCycleData'],subCycleSwap,i)):
                subCycleSwap += 1
                continue

    if (data[i]['miner']['diff'] - feeFromTrans) != validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]['rewardPerBlock']:
        print("reward at block " + str(i) + " for validator " + miner + " is not correct! expected " + str(validatorDict[cycleSwap]['subCycleData'][subCycleSwap]['validators'][miner]['rewardPerBlock']) + " got " + str(data[i]['miner']['diff']))
        if(checkForChange(validatorDict[cycleSwap]['subCycleData'], subCycleSwap,i)):
            subCycleSwap += 1
            continue


    if i % 250 == 0:
        print("atBlock ", str(i))

    if i % 5000 == 0:
        with open('data/results.json', 'w') as fp:
            json.dump(data, fp)

    if i == validatorDict[cycleSwap]['endBlock']:
        print("newCycleStarted block " + str(validatorDict[cycleSwap]['endBlock'] + 1))
        cycleSwap+=1

with open('data/results.json', 'w') as fp:
    json.dump(data, fp)

with open('data/results.csv', 'w') as f:
  w = csv.writer(f)
  w.writerows(data.items())

with open('data/cycleData.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(validatorDict.items())
    print('Done writing cycleData.csv')

with open('data/cycleData.json', 'w') as fp:
    json.dump(validatorDict, fp)
    print('Done writing cycleData.json')

