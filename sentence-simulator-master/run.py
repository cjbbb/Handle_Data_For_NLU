import os
import random

os.system('python main.py -f TreeSum.json -c 117756 -w out/word.txt -s out/sent.txt')

intent2Sents = {}
sent2Slots = {}
ans = []
hashSet = set()
with open('out/word.txt', 'r',encoding='utf-8') as frWords:
    with open('out/sent.txt', 'r',encoding='utf-8') as frSents:
        with open('out/label', 'w',encoding='utf-8') as ftLabel:
            with open('out/seq.in', 'w',encoding='utf-8') as ftSents:
                with open('out/seq.out', 'w',encoding='utf-8') as ftSlots:
                    while (1):
                        sline = frSents.readline()
                        wline = frWords.readline()
                        if not sline:
                            break
                        if not wline:
                            break
                        hashSline = sline.split('\t')
                        hashSline[1] = hashSline[1][0:-1]
                        if hashSline[1] in hashSet:
                            pass
                        else:
                            hashSet.add(hashSline[1])
                            words = wline.split(',')[0:-1]
                            slots = []
                            for key in words:
                                slots.append(key.split('\t')[1])

                            sents = sline.split('\t')
                            sents[1] = sents[1][0:-1]
                            intent2Sents.setdefault(sents[0], [])
                            intent2Sents[sents[0]].append(sents[1])
                            sent2Slots[sents[1]] = ' '.join(slots)
                            if len(slots) != len(words):
                                print('Error '+sline)
                    for intents in intent2Sents:
                        for sent in intent2Sents[intents]:
                            ans.append({
                                'intent': intents,
                                'sents': sent,
                                'slots': sent2Slots[sent]
                            })
                    random.shuffle(ans)
                    for i in ans:
                        ftLabel.write(i['intent'])
                        ftLabel.write('\n')
                        ftSlots.write(i['slots'])
                        ftSlots.write('\n')
                        ftSents.write(i['sents'] )
                        ftSents.write('\n')

                        # ftLabel.write(i['intent'] + '\n')
                        # ftSlots.write(i['slots'] + '\n')
                        # ftSents.write(i['sents'] + '\n')

# 剩余部分 将train.txt加入到输出部分

sum = []
mapSent = {}  # intent->sent
mapSlots = {}  # sent->slots
mapQuerySlots = {}  # sent->not entity words
print("read train.txt from " + os.path.join(os.path.dirname(os.getcwd()), 'newData/train.txt'))
with open(os.path.join(os.path.dirname(os.getcwd()), 'newData/train.txt'), 'r',encoding='utf-8') as Ftest:
    while (1):
        line = Ftest.readline()[0:-1]
        if not line:
            break
        line = eval(line)
        sum.append(line)
        mapSent.setdefault(line['intent'], [])
        mapSent[line['intent']].append(line['query'])
        mapQuerySlots.setdefault(line['query'], [])
        wordSlots = line['query_slot']['token']
        mapQuerySlots[line['query']] = wordSlots
        slots = list(line['slots'])
        tempSlots = {}
        for i in slots:
            tempIO = str(i[0])
            if '.' in i[0]:
                tempIO = tempIO.split('.')[1]
            tempSlots[str(i[1])] = tempIO

        mapSlots[line['query']] = tempSlots

listTest = []
for key in mapSent:
    for value in mapSent[key]:
        listTest.append({
            'intent': key,
            'value': value,
            'slots': mapSlots[value]
        })

random.shuffle(listTest)
with open("out/label", 'a',encoding='utf-8') as wtLabel:
    with open("out/seq.in", 'a',encoding='utf-8') as wtSent:
        with open("out/seq.out", 'a',encoding='utf-8') as wtSlots:
            for i in listTest:
                if i['value'] in hashSet:
                    pass
                else:
                    hashSet.add(i['value'])
                    wtLabel.write(i['intent'] + '\n')
                    wtSent.write(i['value'] + '\n')
                    words = i['value']
                    for j in mapSlots[i['value']]:
                        if ' ' in j:
                            strAns = ''
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
