from web3 import Web3
import csv
import json
from testnetCon import *


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


    vals = fuseConsensusContract.functions.currentValidators().call(block_identifier=i + 20)
    for val in vals:
        validatorDict[cycleCounter][val] = {}
        valCounter += 1



    #work out share and if they have delegates in that cycle
    for val in validatorDict[cycleCounter]:
        delegatorsForVal = fuseConsensusContract.functions.delegators(val).call(block_identifier=i)
        validatorDict[cycleCounter][val]["delegators"] = {}
        sumOfDelegates = 0
        for dele in delegatorsForVal:
            validatorDict[cycleCounter][val]["delegators"][dele] = {}
            delegatedAmount = float(fuseConsensusContract.functions.delegatedAmount(dele,val).call(block_identifier=i)/10**18)
            validatorDict[cycleCounter][val]["delegators"][dele]['Amount'] = delegatedAmount
            sumOfDelegates += delegatedAmount

        stakedAmount = float(fuseConsensusContract.functions.stakeAmount(val).call(block_identifier=i)/10**18)
        validatorDict[cycleCounter][val]['stakedAmount'] = stakedAmount
        validatorDict[cycleCounter][val]['selfStaked'] = stakedAmount - sumOfDelegates
        validatorDict[cycleCounter][val]['fee'] = float(fuseConsensusContract.functions.validatorFee(val).call(block_identifier=i)/10**18)

    totalStakedCycle = 0
    for val in validatorDict[cycleCounter]:
        totalStakedCycle += validatorDict[cycleCounter][val]['stakedAmount']

    for val in validatorDict[cycleCounter]:
        #calc rewards
        validatorDict[cycleCounter][val]['rewardToNode'] = infPerCycle * (validatorDict[cycleCounter][val]['stakedAmount']/totalStakedCycle)
        delegatesRewards = 0
        for dele in validatorDict[cycleCounter][val]["delegators"]:
            validatorDict[cycleCounter][val]["delegators"][dele]['reward'] = validatorDict[cycleCounter][val]['rewardToNode'] * (validatorDict[cycleCounter][val]["delegators"][dele]['Amount'] / validatorDict[cycleCounter][val]['stakedAmount']) * (1-validatorDict[cycleCounter][val]['fee'])
            validatorDict[cycleCounter][val]["delegators"][dele]['rewardPerBlock'] = round((validatorDict[cycleCounter][val]["delegators"][dele]['reward']/cycleDuration) * valCounter,6)
            delegatesRewards += validatorDict[cycleCounter][val]["delegators"][dele]['reward']
        validatorDict[cycleCounter][val]['reward'] = validatorDict[cycleCounter][val]['rewardToNode'] - delegatesRewards
        validatorDict[cycleCounter][val]['rewardPerBlock'] = round((validatorDict[cycleCounter][val]['reward']/cycleDuration) * valCounter,6)


    #skew the start if we have had new or left validators
    itr = 0
    if(cycleCounter != 0):
        if (len(validatorDict[cycleCounter]) != (len(validatorDict[cycleCounter-1])-4)):
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
    data[i]['miner']['expectedReward'] = validatorDict[cycleSwap][miner]['rewardPerBlock']
    data[i]['miner']['transFees'] = feeFromTrans
    data[i]['delegator'] = {}

    for dele in validatorDict[cycleSwap][miner]["delegators"]:
        data[i]['delegator'][dele] = {}
        data[i]['delegator'][dele]['balanceBefore'] = float(web3Fuse.eth.getBalance(dele, i - 1) / 10 ** 18)
        data[i]['delegator'][dele]['balanceNow'] = float(web3Fuse.eth.getBalance(dele, i) / 10 ** 18)
        diff = (data[i]['delegator'][dele]['balanceNow']) - (data[i]['delegator'][dele]['balanceBefore'])
        data[i]['delegator'][dele]['diff'] = round(diff, 6)
        data[i]['delegator'][dele]['expectedReward'] = validatorDict[cycleSwap][miner]["delegators"][dele]['rewardPerBlock']
        if data[i]['delegator'][dele]['diff'] != validatorDict[cycleSwap][miner]["delegators"][dele]['rewardPerBlock']:
            print("reward at block " + str(i) + " for delegator " + dele + " is not correct! expected " + str(validatorDict[cycleSwap][miner]["delegators"][dele]['rewardPerBlock']) + " got " + str(data[i]['delegator'][dele]['diff']))

    if (data[i]['miner']['diff'] - feeFromTrans) != validatorDict[cycleSwap][miner]['rewardPerBlock']:
        print("reward at block " + str(i) + " for validator " + miner + " is not correct! expected " + str(validatorDict[cycleSwap][miner]['rewardPerBlock']) + " got " + str(data[i]['miner']['diff']))

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

