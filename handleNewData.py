ansList = []
entityMap = {}  # entity -> content
intentSet = set()

def run():
    with open('snips/train/label', 'r', encoding='utf-8')as frLabel:
        with open('snips/train/seq.in', 'r', encoding='utf-8')as frSent:
            with open('snips/train/seq.out', 'r', encoding='utf-8')as frSlots:
                with open('newData/train.txt', 'w', encoding='utf-8') as fw:
                    while (1):
                        labelLine = frLabel.readline()[0:-1]
                        sentLine = frSent.readline()[0:-1]
                        slotsLine = frSlots.readline()[0:-2]  # 空格
                        if not slotsLine:
                            break

                        slots, querySlots = handleSlots(slotsLine, sentLine)
                        ansList.append({
                            'intent': labelLine,
                            'query': sentLine,
                            'slots': slots,
                            'querySlots': querySlots
                        })
                        fw.write('%s\n' % str({'intent': labelLine,
                                               'query': sentLine,
                                               'slots': slots,
                                               'query_slot': querySlots}))


def handleSlots(slotsLine, sentLine):
    ansSet = set()
    ansDict = {}
    entityList = []
    token = []
    sp = []
    start = 0
    slots = slotsLine.split(' ')
    words = sentLine.split(' ')
    for slot in slots:
        entityMap.setdefault(slot[2:], [])
    for i in range(len(slots)):
        if slots[i][0] == 'B':
            tempWords = []
            tempWords.append(words[i])
            j = i + 1
            while (j < len(slots)):
                if (slots[j][0] != 'I'):
                    break
                else:
                    tempWords.append(words[j])
                    j += 1
            word = ' '.join(tempWords)
            entityMap[slots[i][2:]].append(word)
            entityList.append(slots[i][2:])
            ansSet.add((str(i) + '.' + slots[i][2:], word))
            token.append('<' + slots[i][2:] + '>')
            sp.append((start, len(token) - 1))
            start = len(token)
        else:
            token.append(words[i])

    sp.append((start, len(token)))
    ansDict['feature'] = tuple(entityList)  # querySlots/feature
    ansDict['token'] = token
    ansDict['sp'] = sp
    return ansSet, ansDict


def genEntity():
    for key in entityMap:
        if len(key) >=1: #可能出现’‘
            with open('newData/active_entities/'+key,'w',encoding='utf-8') as fw:
                for value in entityMap[key]:
                    fw.write(value+'\n')


if __name__ == "__main__":
    run()
    print('已生成train.txt')
    genEntity()
    print('已生成Entity，共有'+str(len(entityMap)-1)+'个entity')

