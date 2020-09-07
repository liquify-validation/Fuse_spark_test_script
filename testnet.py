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



inflation = blockRewardContract.functions.getInflation().call()
blocksPerYear = blockRewardContract.functions.getBlocksPerYear().call()

initSupply = 300000000


cycleCounter = 0

i = 50000

validatorDict = {}
upToo = 0


#get the validators per cycle
#for i in range (165980,newBlock,cycleDuration):
while i < newBlock:
    valCounter = 0
    validatorDict[cycleCounter] = {}
    cycleDuration = fuseConsensusContract.functions.getCycleDurationBlocks().call(block_identifier=i)
    infPerYear = initSupply * (inflation / 100)
    infPerCycle = (infPerYear / blocksPerYear) * cycleDuration

    vals = fuseConsensusContract.functions.currentValidators().call(block_identifier=i)
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


    validatorDict[cycleCounter]['startBlock'] = fuseConsensusContract.functions.getCurrentCycleStartBlock().call(block_identifier=i)
    validatorDict[cycleCounter]['endBlock'] = fuseConsensusContract.functions.getCurrentCycleEndBlock().call(block_identifier=i) - 1

    start = fuseConsensusContract.functions.getCurrentCycleStartBlock().call(block_identifier=i)
    end = fuseConsensusContract.functions.getCurrentCycleStartBlock().call(block_identifier=i) + cycleDuration
    i = fuseConsensusContract.functions.getCurrentCycleEndBlock().call(block_identifier=i) + 1
    cycleCounter += 1
    upToo = i

with open('cycleData.csv', 'w') as f:
    w = csv.writer(f)
    w.writerows(validatorDict.items())

data = {}
cycleSwap = 0


for i in range (50000, upToo, 1):
    miner = web3Fuse.eth.getBlock(i)['miner']
    data[i] = {}
    data[i]['miner'] = {}
    data[i]['miner']['node'] = miner
    data[i]['miner']['balanceBefore'] = float(web3Fuse.eth.getBalance(miner,i-1)/10**18)
    data[i]['miner']['balanceNow'] = float(web3Fuse.eth.getBalance(miner, i)/10**18)
    diff = (data[i]['miner']['balanceNow']) - (data[i]['miner']['balanceBefore'])
    data[i]['miner']['diff'] = round(diff,6)
    data[i]['miner']['expectedReward'] = validatorDict[cycleSwap][miner]['rewardPerBlock']
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

    if data[i]['miner']['diff'] != validatorDict[cycleSwap][miner]['rewardPerBlock']:
        print("reward at block " + str(i) + " for validator " + miner + " is not correct! expected " + str(validatorDict[cycleSwap][miner]['rewardPerBlock']) + " got " + str(data[i]['miner']['diff']))

    if i % 100 == 0:
        print("atBlock ", str(i))

    if i == validatorDict[cycleSwap]['endBlock']:
        print("newCycleStarted block " + str(validatorDict[cycleSwap]['endBlock'] + 1))
        cycleSwap+=1

with open('results.json', 'w') as fp:
    json.dump(data, fp)

with open('results.csv', 'w') as f:
  w = csv.writer(f)
  w.writerows(data.items())
