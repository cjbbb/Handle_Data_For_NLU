import random
import os

intentSet = set()
entitySet = set()
intentFile = os.listdir('data/active_packages')
entityFile = os.listdir('data/active_entities')
for i in intentFile:
    i = i[0:-5]
    if i not in intentSet:
        intentSet.add(i)
print("load " + str(len(intentSet)) + " intents")

for i in entityFile:
    if i not in entitySet:
        entitySet.add(i)
print("load " + str(len(entitySet)) + " entities")
print(entitySet)

mapSent = {}  # intent->sent
mapSlots = {}  # sent->slots
mapQuerySlots = {}  # sent->not entity words
with open('data/test.txt', 'r') as Ftest:
    while (1):
        line = Ftest.readline()[0:-1]
        if not line:
            break
        line = eval(line)
        if line['intent'] in intentSet:
            slots = list(line['slots'])
            tempSlots = {}
            entityFlag = False
            for i in slots:
                tempIO = str(i[0])
                if '.' in i[0]:
                    tempIO = tempIO.split('.')[1]
                tempSlots[str(i[1])] = tempIO
                if tempIO not in entitySet:
                    entityFlag = True
                    print("error entity:" + tempIO)
            if entityFlag == False:
                mapSlots[line['query']] = tempSlots
                mapSent.setdefault(line['intent'], [])
                mapSent[line['intent']].append(line['query'])
                mapQuerySlots.setdefault(line['query'], [])
                wordSlots = line['query_slot']['token']
                mapQuerySlots[line['query']] = wordSlots
        else:
            print("Wrong Intent " + line['intent'])

listTest = []
listDev = []
for key in mapSent:
    count = len(mapSent[key]) / 2
    i = 0
    for value in mapSent[key]:
        i += 1
        if (i <= count):
            listTest.append({
                'intent': key,
                'value': value,
                'slots': mapSlots[value]
            })
        else:
            listDev.append({
                'intent': key,
                'value': value,
                'slots': mapSlots[value]
            })
random.shuffle(listTest)
random.shuffle(listDev)
with open("data/testOut/test/label", 'w') as wtLabel:
    with open("data/testOut/test/seq.in", 'w') as wtSent:
        with open("data/testOut/test/seq.out", 'w') as wtSlots:
            for i in listTest:
                wtLabel.write(i['intent'] + '\n')
                wtSent.write(i['value'] + '\n')
                words = i['value']
                for j in mapSlots[i['value']]:
                    if ' ' in j:
                        splits = j.split(' ')
                        strAns = 'B-' + mapSlots[i['value']][j]
                        for count in range(len(splits) - 1):
                            strAns += ' I-' + mapSlots[i['value']][j]

                        words = words.replace(j, strAns, 1)
                    else:
                        wordSplits = words.split(' ')
                        for temp in range(len(wordSplits)):
                            if wordSplits[temp] == j:
                                wordSplits[temp] = 'B-' + str(mapSlots[i['value']][j])

                        words = ' '.join(wordSplits)

                wordSlots = words.split(' ')
                ans = []
                for i in wordSlots:
                    if len(i) >= 2:
                        if ((i[0] == 'I') | (i[0] == 'B')) & (i[1] == '-'):
                            ans.append(i)
                        else:
                            ans.append('O')
                    else:
                        ans.append('O')
                words = ' '.join(ans)
                wtSlots.write(words + '\n')

with open("data/testOut/valid/label", 'w') as wtLabel:
    with open("data/testOut/valid/seq.in", 'w') as wtSent:
        with open("data/testOut/valid/seq.out", 'w') as wtSlots:
            for i in listDev:
                wtLabel.write(i['intent'] + '\n')
                wtSent.write(i['value'] + '\n')
                words = i['value']
                for j in mapSlots[i['value']]:
                    if ' ' in j:
                        splits = j.split(' ')
                        strAns = 'B-' + mapSlots[i['value']][j]
                        for count in range(len(splits) - 1):
                            strAns += ' I-' + mapSlots[i['value']][j]

                        wordSplits = words.split(' ')
                        wordSplits = words.split(' ')
                        for temp in range(len(wordSplits)):
                            if wordSplits[temp] == j:
                                wordSplits[temp] = strAns
                        words = ' '.join(wordSplits)
                    else:
                        wordSplits = words.split(' ')
                        for temp in range(len(wordSplits)):
                            if wordSplits[temp] == j:
                                wordSplits[temp] = 'B-' + str(mapSlots[i['value']][j])
                        words = ' '.join(wordSplits)

                wordSlots = words.split(' ')
                ans = []
                for i in wordSlots:
                    if len(i) >= 2:
                        if ((i[0] == 'I') | (i[0] == 'B')) & (i[1] == '-'):
                            ans.append(i)
                        else:
                            ans.append('O')
                    else:
                        ans.append('O')
                words = ' '.join(ans)
                wtSlots.write(words + '\n')
