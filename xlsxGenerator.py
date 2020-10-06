import json
import xlsxwriter

with open("data/results.json") as json_file:
    data = json.load(json_file)

with open("data/cycleData.json") as json_file:
    cycledata = json.load(json_file)

with open("data/transactionData.json") as json_file:
    transdata = json.load(json_file)

workbook = xlsxwriter.Workbook('data/results.xlsx')
worksheet = workbook.add_worksheet()

worksheet.set_column('A:Z', 30)

headers = ['cycle','subcycle','startBlock','endBlock','address','isVal','startBalance','endBalance','in/out trans','stake','delegated','totalNetworkStake','del fee','blocksMinedInCycle', 'rewardPerBlock', 'totalTransFees','calculateRewards', 'actualRewards', 'diff']

horPos = ord('A')
vertPos = 1

for header in headers:
    worksheet.write(chr(horPos)+str(vertPos),header)
    horPos += 1

horPos = ord('A')
vertPos += 1

for cycle in cycledata:
    if int(cycle) < 122:
        for subCycle in cycledata[cycle]['subCycleData']:
            for val in cycledata[cycle]['subCycleData'][subCycle]['validators']:
                worksheet.write('A' + str(vertPos), cycle)
                worksheet.write('B' + str(vertPos), subCycle)
                worksheet.write('C' + str(vertPos), str(cycledata[cycle]['subCycleData'][subCycle]['startBlock']))
                worksheet.write('D' + str(vertPos), str(cycledata[cycle]['subCycleData'][subCycle]['endBlock']))
                worksheet.write('E' + str(vertPos), str(val))
                worksheet.write('F' + str(vertPos), "True")

                numVals = len(cycledata[cycle]['subCycleData'][subCycle]['validators'])

                found = False
                blockSearched = 0
                for i in range(cycledata[cycle]['subCycleData'][subCycle]['startBlock'],cycledata[cycle]['subCycleData'][subCycle]['startBlock']+numVals):
                    if data[str(i)]['miner']['node'] == val:
                        blockSearched = i
                        found = True
                        worksheet.write('G' + str(vertPos), (data[str(i)]['miner']['balanceBefore']))
                        break

                foundEnd = False
                blockSearchedEnd = 0
                for i in range(cycledata[cycle]['subCycleData'][subCycle]['endBlock'], cycledata[cycle]['subCycleData'][subCycle]['endBlock'] - numVals, -1):
                    if data[str(i)]['miner']['node'] == val:
                        blockSearchedEnd = i
                        foundEnd = True
                        worksheet.write('H' + str(vertPos), (data[str(i)]['miner']['balanceNow']))
                        break

                transAmount = 0

                for trans in transdata['validators'][val]['to']:
                    if int(trans) > cycledata[cycle]['subCycleData'][subCycle]['startBlock'] and int(trans) < cycledata[cycle]['subCycleData'][subCycle]['endBlock']:
                        for transItr in range (1,transdata['validators'][val]['to'][trans]['transCount']+1):
                            transAmount += transdata['validators'][val]['to'][trans][str(transItr)]['value']

                for trans in transdata['validators'][val]['from']:
                    if int(trans) > cycledata[cycle]['subCycleData'][subCycle]['startBlock'] and int(trans) < cycledata[cycle]['subCycleData'][subCycle]['endBlock']:
                        for transItr in range (1,transdata['validators'][val]['from'][trans]['transCount']+1):
                            transAmount -= transdata['validators'][val]['from'][trans][str(transItr)]['value']
                            transAmount -= transdata['validators'][val]['from'][trans][str(transItr)]['transFee']

                worksheet.write('I' + str(vertPos), (transAmount))

                worksheet.write('J' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['selfStaked']))
                worksheet.write('K' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['stakedAmount'] - cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['selfStaked']))
                worksheet.write('L' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['totalStaked']))
                worksheet.write('M' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['fee']))

                blocks = cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['blockCounter']
                rewardPerBlock = cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['rewardPerBlock']

                worksheet.write('N' + str(vertPos), blocks)
                worksheet.write('O' + str(vertPos), rewardPerBlock)

                #calc transactionFees
                transFees = 0
                for transactionFee in range(int(cycledata[cycle]['subCycleData'][subCycle]['startBlock']),int(cycledata[cycle]['subCycleData'][subCycle]['endBlock'])):
                    if data[str(transactionFee)]['miner']['node'] == val:
                        transFees += data[str(transactionFee)]['miner']['transFees']

                worksheet.write('P' + str(vertPos), transFees)

                worksheet.write('Q' + str(vertPos), blocks*rewardPerBlock)
                string = "=H"+str(vertPos)+" - G"+str(vertPos)
                worksheet.write_formula('R' + str(vertPos),  ("=H"+str(vertPos)+" - G"+str(vertPos) + " - I"+str(vertPos)+ " - P"+str(vertPos)))
                string = "=O" + str(vertPos) + " - N" + str(vertPos)
                worksheet.write_formula('S' + str(vertPos),  ("=ROUND(Q" + str(vertPos) + " - R" + str(vertPos)+",4)"))

                vertPos+=1
                for delegate in cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['delegators']:
                    worksheet.write('A' + str(vertPos), cycle)
                    worksheet.write('B' + str(vertPos), subCycle)
                    worksheet.write('C' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['startBlock']))
                    worksheet.write('D' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['endBlock']))
                    worksheet.write('E' + str(vertPos), str(delegate))
                    worksheet.write('F' + str(vertPos), "False")
                    if(found and foundEnd):
                        worksheet.write('G' + str(vertPos), (data[str(blockSearched)]['delegator'][delegate]['balanceBefore']))
                        worksheet.write('H' + str(vertPos), (data[str(blockSearchedEnd)]['delegator'][delegate]['balanceNow']))

                        transAmount = 0

                        for trans in transdata['delegators'][delegate]['to']:
                            if int(trans) > cycledata[cycle]['subCycleData'][subCycle]['startBlock'] and int(trans) < cycledata[cycle]['subCycleData'][subCycle]['endBlock']:
                                for transItr in range(1, transdata['delegators'][delegate]['to'][trans]['transCount'] + 1):
                                    transAmount += transdata['delegators'][delegate]['to'][trans][str(transItr)]['value']

                        for trans in transdata['delegators'][delegate]['from']:
                            if int(trans) > cycledata[cycle]['subCycleData'][subCycle]['startBlock'] and int(trans) < cycledata[cycle]['subCycleData'][subCycle]['endBlock']:
                                for transItr in range(1, transdata['delegators'][delegate]['from'][trans]['transCount'] + 1):
                                    transAmount -= transdata['delegators'][delegate]['from'][trans][str(transItr)]['value']
                                    transAmount -= transdata['delegators'][delegate]['from'][trans][str(transItr)]['transFee']

                        worksheet.write('I' + str(vertPos), (transAmount))

                        worksheet.write('K' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['delegators'][delegate]['Amount']))
                        worksheet.write('L' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['totalStaked']))
                        worksheet.write('M' + str(vertPos), (cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['fee']))
                        rewardPerBlock = cycledata[cycle]['subCycleData'][subCycle]['validators'][val]['delegators'][delegate]['rewardPerBlock']

                        worksheet.write('N' + str(vertPos), blocks)
                        worksheet.write('O' + str(vertPos), rewardPerBlock)

                        # calc transactionFees
                        transFees = 0

                        worksheet.write('P' + str(vertPos), transFees)

                        worksheet.write('Q' + str(vertPos), blocks * rewardPerBlock)
                        string = "=H" + str(vertPos) + " - G" + str(vertPos)
                        worksheet.write_formula('R' + str(vertPos), ("=H" + str(vertPos) + " - G" + str(vertPos) + " - I" + str(vertPos) + " - P" + str(vertPos)))
                        string = "=O" + str(vertPos) + " - N" + str(vertPos)
                        worksheet.write_formula('S' + str(vertPos), ("=ROUND(Q" + str(vertPos) + " - R" + str(vertPos) + ",4)"))

                    vertPos += 1

workbook.close()