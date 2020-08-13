import json
import os

entities = os.listdir('newData/active_entities')
entitylist = []
tempCount = 0
for temp in entities:
    tempCount += 1
    entitylist.append({
        "agent_id": "5c48306bc4952fdf7150e1a9",
        "description": "",
        "id": str(tempCount),
        "name": temp
    })

entitymap = {}
for item in entitylist:
    entitymap[item['name']] = item['id']


def auto_rules(query_list):
    d = {}
    for item in query_list:
        result = item['query_slot']
        d.setdefault(result['feature'], [])
        d[result['feature']].append(result)
    count = 0
    rules = []
    for slots, result_list in d.items():
        count += 1
        rule = {
            'name': 'rule' + str(count),
            'type': 'order',
            'nodes': []
        }
        nodes = rule['nodes']
        dropout = [0.0 for _ in range(len(slots) + 1)]
        content = [[] for _ in range(len(slots) + 1)]
        for result in result_list:
            # feature 相同的每个result
            for i in range(len(result['sp'])):
                sp = result['sp'][i]
                if len(result['token'][sp[0]:sp[1]]) > 0:
                    content[i].append(' '.join(result['token'][sp[0]:sp[1]]))
                else:
                    dropout[i] += 1
        nodes.append({
            'type': 'content',
            'value': ' | '.join(list(content[0])),
            'dropout': dropout[0] / len(result_list)
        })
        for i in range(len(slots)):
            nodes.append({
                'type': 'entity',
                'value': slots[i],
                'slot': slots[i],
                'dropout': 0.0
            })
            nodes.append({
                'type': 'content',
                'value': ' | '.join(list(content[i + 1])),
                'dropout': dropout[i + 1] / len(result_list)
            })

        rules.append(rule)
    return rules


def make_package(
        entitymap,
        rules,
        name='quantity',
        weight=0.01):
    import json
    package = {
        'intent': name,
        'type': 'intent',
        'weight': weight,
        'children': [
            {
                "type": "holder"
            }
        ]

    }
    children = package['children']
    entityCount = {}
    count = 0
    entityLots = []  # 最多的entity
    for rule in rules:
        for node in rule['nodes']:
            if (node['type'] == 'entity'):
                entityName = node['value']
                if entityCount.__contains__(entityName) == True:
                    tempNumber = entityCount[entityName]
                    entityCount[entityName] = tempNumber + 1
                if entityCount.__contains__(entityName) == False:
                    count += 1
                    entityCount
                    entityCount[entityName] = 1
    for entityKey in entityCount:
        if entityCount[entityKey] > count * 0.955:
            entityLots.append(entityKey)

    e2p = {}  # entities 2 pickone {{entity}:rule}
    for rule in rules:
        tempEntities = ''

        for i in range(len(rule['nodes'])):
            if (rule['nodes'][i]['type'] == 'entity') & \
                    (rule['nodes'][i]['dropout'] < 1) & \
                    (entityLots.__contains__(rule['nodes'][i]['value']) == True):
                tempEntities += rule['nodes'][i]['value']
                tempEntities += '|'
        e2p.setdefault(tempEntities, [])
        e2p[tempEntities].append(rule)

    for poKey in e2p:
        if len(e2p[poKey]) > 1:
            print(name)
        child = {
            'type': 'order',
            'name': rule['name'],
            'dropout': 0,
            'children': []
        }
        children.append(child)
        orderChildrens = child['children']

        if (poKey == ''):  # doesnt have any special entities
            # print(e2p)
            children.remove(child)
            for rule in e2p[poKey]:
                s1Child = {  # special 1 child
                    'type': 'order',
                    'name': rule['name'],
                    'dropout': 0,
                    'children': []
                }
                children.append(s1Child)
                s1Childrens = s1Child['children']
                for node in rule['nodes']:
                    if node['dropout'] < 1.0:
                        if node['type'] == 'content':
                            content = node['value'].split(' | ')
                            contents = {}
                            for temp in content:
                                if contents.__contains__(temp):
                                    tempValue = contents[temp]
                                    contents[temp] = tempValue + 1
                                else:
                                    contents[temp] = 1
                            s1Childrens.append({
                                # Todo
                                'content': contents,
                                'type': 'content',
                                'cut': 0,
                                'name': content,
                                'dropout': node['dropout']
                            })

                        elif node['type'] == 'entity':
                            s1Childrens.append({
                                'type': 'content',
                                'cut': 0,
                                'isSlot': True,
                                'name': '<%s>' % node['value'],
                                'entity': entitymap[node['value']],
                                'slot': node['slot']
                            })
        else:
            poKeys = poKey.split('|')[0:-1]
            for entities in poKeys:
                s2Child = {  # pickone
                    'type': 'pickone',
                    'name': rule['name'],
                    'dropout': 0,
                    'children': []
                }
                s2Childrens = s2Child['children']
                entityNode = {}
                pickoneWeight = {}

                for rule in e2p[poKey]:
                    # rule 是一句话
                    s3Child = {  # special 1 child
                        'type': 'order',
                        'name': rule['name'],
                        'dropout': 0,
                        'children': []
                    }
                    s3Childrens = s3Child['children']

                    count = 0

                    for node in rule['nodes']:
                        if (node['type'] == 'entity') & (node['value'] == entities):
                            break;
                        count += 1
                    deleteList = []
                    for node in rule['nodes']:
                        deleteList.append(node)
                        if node['dropout'] < 1.0:
                            if node['type'] == 'content':
                                content = node['value'].split(' | ')
                                contents = {}
                                for temp in content:
                                    if contents.__contains__(temp):
                                        tempValue = contents[temp]
                                        contents[temp] = tempValue + 1
                                    else:
                                        contents[temp] = 1
                                temp1 = {
                                    'content': contents,
                                    'type': 'content',
                                    'cut': 0,
                                    'name': content[0],
                                    'dropout': node['dropout']
                                }
                                if count > 1:
                                    s3Childrens.append(temp1)
                                else:
                                    if pickoneWeight.__contains__(str(temp1)):
                                        tempCount = pickoneWeight[str(temp1)]
                                        pickoneWeight[str(temp1)] = tempCount + 1
                                    else:
                                        pickoneWeight[str(temp1)] = 1

                            elif (node['type'] == 'entity') & (node['value'] != entities):
                                temp2 = {
                                    'type': 'content',
                                    'cut': 0,
                                    'isSlot': True,
                                    'name': '<%s>' % node['value'],
                                    'entity': entitymap[node['value']],
                                    'slot': node['slot']
                                }
                                if count > 1:
                                    s3Childrens.append(temp2)
                                else:
                                    if pickoneWeight.__contains__(str(temp2)):
                                        tempCount = pickoneWeight[str(temp2)]
                                        pickoneWeight[str(temp2)] = tempCount + 1
                                    else:
                                        pickoneWeight[str(temp2)] = 1

                            elif (node['type'] == 'entity') & (node['value'] == entities):
                                entityNode = {
                                    'type': 'content',
                                    'cut': 0,
                                    'isSlot': True,
                                    'name': '<%s>' % node['value'],
                                    'entity': entitymap[node['value']],
                                    'slot': node['slot']
                                }
                                break

                    for i in deleteList:
                        rule['nodes'].remove(i)

                    if count > 1:
                        if pickoneWeight.__contains__(str(s3Child)):
                            tempCount = pickoneWeight[str(s3Child)]
                            pickoneWeight[str(s3Child)] = tempCount + 1
                        else:
                            pickoneWeight[str(s3Child)] = 1
                weightSum = 0
                for temp in pickoneWeight.keys():
                    weightSum += pickoneWeight[temp]
                for tempKey in pickoneWeight.keys():
                    key = eval(tempKey)
                    if (key['type'] == 'order'):
                        s2Childrens.append({
                            'type': 'order',
                            'name': key['name'],
                            'dropout': key['dropout'],
                            'children': key['children'],
                            'weight': pickoneWeight[tempKey] / weightSum
                        })
                    elif (key['type'] == 'content'):
                        if key.__contains__('isSlot'):
                            s2Childrens.append({
                                'type': 'content',
                                'cut': key['cut'],
                                'isSlot': key['isSlot'],
                                'name': key['name'],
                                'entity': key['entity'],
                                'slot': key['slot'],
                                'weight': pickoneWeight[tempKey] / weightSum
                            })
                        else:
                            s2Childrens.append({
                                'content': key['content'],
                                'type': 'content',
                                'cut': key['cut'],
                                'name': key['name'],
                                'dropout': key['dropout'],
                                'weight': pickoneWeight[tempKey] / weightSum
                            })
                if len(s2Child['children']) > 0:
                    orderChildrens.append(s2Child)
                orderChildrens.append(entityNode)

            s4Child = {  # pickone
                'type': 'pickone',
                'name': rule['name'],
                'dropout': 0,
                'children': []
            }
            pickoneWeight = {}
            s4Childrens = s4Child['children']
            for rule in e2p[poKey]:
                # rule 是一句话
                s5Child = {  # special 1 child
                    'type': 'order',
                    'name': rule['name'],
                    'dropout': 0,
                    'children': []
                }
                s5Childrens = s5Child['children']

                count = len(rule['nodes'])
                for node in rule['nodes']:
                    if node['dropout'] < 1.0:
                        if node['type'] == 'content':
                            content = node['value'].split(' | ')
                            contents = {}
                            for temp in content:
                                if contents.__contains__(temp):
                                    tempValue = contents[temp]
                                    contents[temp] = tempValue + 1
                                else:
                                    contents[temp] = 1
                            temp1 = {
                                'content': contents,
                                'type': 'content',
                                'cut': 0,
                                'name': content[0],
                                'dropout': node['dropout']
                            }
                            if count > 1:
                                s5Childrens.append(temp1)
                            else:
                                if pickoneWeight.__contains__(str(temp1)):
                                    tempCount = pickoneWeight[str(temp1)]
                                    pickoneWeight[str(temp1)] = tempCount + 1
                                else:
                                    pickoneWeight[str(temp1)] = 1

                        elif (node['type'] == 'entity'):
                            temp2 = {
                                'type': 'content',
                                'cut': 0,
                                'isSlot': True,
                                'name': '<%s>' % node['value'],
                                'entity': entitymap[node['value']],
                                'slot': node['slot']
                            }
                            if count > 1:
                                s5Childrens.append(temp2)
                            else:
                                if pickoneWeight.__contains__(str(temp2)):
                                    tempCount = pickoneWeight[str(temp2)]
                                    pickoneWeight[str(temp2)] = tempCount + 1
                                else:
                                    pickoneWeight[str(temp2)] = 1

                if count > 1:
                    if pickoneWeight.__contains__(str(s5Child)):
                        tempCount = pickoneWeight[str(s5Child)]
                        pickoneWeight[str(s5Child)] = tempCount + 1
                    else:
                        pickoneWeight[str(s5Child)] = 1
            weightSum = 0
            for temp in pickoneWeight.keys():
                weightSum += pickoneWeight[temp]
            for tempKey in pickoneWeight.keys():
                key = eval(tempKey)
                if (key['type'] == 'order'):
                    s4Childrens.append({
                        'type': 'order',
                        'name': key['name'],
                        'dropout': key['dropout'],
                        'children': key['children'],
                        'weight': pickoneWeight[tempKey] / weightSum
                    })
                elif (key['type'] == 'content'):
                    if key.__contains__('isSlot'):
                        s4Childrens.append({
                            'type': 'content',
                            'cut': key['cut'],
                            'isSlot': key['isSlot'],
                            'name': key['name'],
                            'entity': key['entity'],
                            'slot': key['slot'],
                            'weight': pickoneWeight[tempKey] / weightSum
                        })
                    else:
                        s4Childrens.append({
                            'content': key['content'],
                            'type': 'content',
                            'cut': key['cut'],
                            'name': key['name'],
                            'dropout': key['dropout'],
                            'weight': pickoneWeight[tempKey] / weightSum
                        })
            if len(s4Childrens) > 0:
                orderChildrens.append(s4Child)

    return json.dumps(package)


train = {}
count = 0

with open('newData/train.txt', 'r', encoding='utf-8') as fin:
    for line in fin:
        count += 1
        query = eval(line)
        train.setdefault(query['intent'], [])
        train[query['intent']].append(query)

for kind in train:
    with open('newData/active_packages/%s' % kind + '.json', 'w', encoding='utf-8') as fout:
        weight = 1.0 * len(train[kind]) / count
        if weight < 0.01:
            weight = 0.01
        fout.write(make_package(
            entitymap,
            auto_rules(train[kind]),
            name=kind,
            weight=weight))
