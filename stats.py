import os
import pickle

DATA_DIR = 'data'

def load_ds(fname='atis.train.pkl'):
  with open(fname, 'rb') as stream:
    ds, dicts = pickle.load(stream)
  print('Done  loading: ', fname)
  print('      samples: {:4d}'.format(len(ds['query'])))
  print('   vocab_size: {:4d}'.format(len(dicts['token_ids'])))
  print('   slot count: {:4d}'.format(len(dicts['slot_ids'])))
  print(' intent count: {:4d}'.format(len(dicts['intent_ids'])))
  return ds, dicts

train_ds, dicts = load_ds(os.path.join(DATA_DIR, 'atis.train.pkl'))
test_ds, dicts = load_ds(os.path.join(DATA_DIR, 'atis.test.pkl'))

t2i, s2i, in2i = map(dicts.get, ['token_ids', 'slot_ids','intent_ids'])
i2t, i2s, i2in = map(lambda d: {d[k]: k for k in d.keys()}, [t2i, s2i, in2i])

query, slots, intent = map(train_ds.get, ['query', 'slot_labels', 'intent_labels'])

def print_i(i):
  print('{:4d}:{:>15}: {}'.format(i, i2in[intent[i][0]],
                                    ' '.join(map(i2t.get, query[i]))))
  for j in range(len(query[i])):
      print('{:>33} {:>40}'.format(i2t[query[i][j]],
                                    i2s[slots[i][j]]  ))
  print('*' * 74)

# for i in range(1140, 1145):
#   print_i(i)

def gen_querys(ds, fname='query.txt'):
  query, intent = map(ds.get, ['query', 'intent_labels'])
  with open(fname, 'w', encoding='utf-8') as fout:
    for i in range(len(query)):
      fout.write('%s\t%s\n' % (i2in[intent[i][0]], ' '.join(map(i2t.get, query[i][1:-1]))))

def print_query_with_slot(i):
  token = []
  for j in range(1, len(query[i]) - 1):
    if i2s[slots[i][j]].startswith('I-'):
      continue
    elif i2s[slots[i][j]].startswith('B-'):
      stat = i2s[slots[i][j]][2:].split('.')[-1]
      token.append('<%s>' % stat)
    else:
      token.append(i2t[query[i][j]])
  print(' '.join(token))

def gen_query_slot(ds, i):
  query, slots = map(ds.get, ['query', 'slot_labels'])
  token = []
  feature = []
  start = 0
  sp = []
  for j in range(1, len(query[i]) - 1):
    if i2s[slots[i][j]].startswith('I-'):
      continue
    elif i2s[slots[i][j]].startswith('B-'):
      feature.append(slots[i][j])
      stat = i2s[slots[i][j]][2:].split('.')[-1]
      token.append('<%s>' % stat)
      sp.append((start, len(token) - 1))
      start = len(token)
    else:
      token.append(i2t[query[i][j]])
  sp.append((start, len(token)))
  return {
    'feature': tuple(feature),
    'token': token,
    'sp': sp
  }

def gen_slots(ds, entity_dir='data'):
  query, slots = map(ds.get, ['query', 'slot_labels'])
  d_slot = {}
  for i in range(len(query)):
    stat = None
    token = []
    for j in range(len(query[i])):
      if i2s[slots[i][j]].startswith('B-'):
        if len(token) > 0:
          stat = stat.split('.')[-1]
          d_slot.setdefault(stat, set())
          d_slot[stat].add(' '.join(token))
        stat = i2s[slots[i][j]][2:]
        token = [i2t[query[i][j]]]
      elif i2s[slots[i][j]].startswith('I-'):
        if stat != i2s[slots[i][j]][2:]:
          raise Exception('Looks like something went wrong')
        token.append(i2t[query[i][j]])
    if len(token) > 0:
      stat = stat.split('.')[-1]
      d_slot.setdefault(stat, set())
      d_slot[stat].add(' '.join(token))
    stat = i2s[slots[i][j]][2:]
  for c in d_slot:
    with open(os.path.join(entity_dir, c), 'w', encoding='utf-8') as fout:
      for item in d_slot[c]:
        fout.write('%s\n' % item)

def gen_dataset(ds, out):
  query, slots, intent = map(ds.get, ['query', 'slot_labels', 'intent_labels'])
  with open(out, 'w', encoding='utf-8') as fout:
    for i in range(len(query)):
      slot = set()
      stat = None
      token = []
      for j in range(len(query[i])):
        if i2s[slots[i][j]].startswith('B-'):
          if len(token) > 0:
            slot.add((stat, ' '.join(token)))
          stat = i2s[slots[i][j]][2:]
          token = [i2t[query[i][j]]]
        elif i2s[slots[i][j]].startswith('I-'):
          if stat != i2s[slots[i][j]][2:]:
            raise Exception('Looks like something went wrong')
          token.append(i2t[query[i][j]])
      if len(token) > 0:
        slot.add((stat, ' '.join(token)))
      fout.write('%s\n' % str({
        'intent': i2in[intent[i][0]],
        'query': ' '.join(map(i2t.get, query[i][1:-1])),
        'slots': slot,
        'query_slot': gen_query_slot(ds, i)
      }))

def auto_rules(func):
  query, slots, intent = map(train_ds.get, ['query', 'slot_labels', 'intent_labels'])
  d = {}
  matched = 0
  for i in range(len(query)):
    if func(intent[i][0]):
      matched += 1
      result = gen_query_slot(i)
      d.setdefault(result['feature'], [])
      d[result['feature']].append(result)
  count = 0
  rules = []
  for slots, result_list in d.items():
    count += 1
    rule = {
      'name': 'rule' + str(count),
      'nodes': []
    }
    nodes = rule['nodes']
    dropout = [0.0 for _ in range(len(slots) + 1)]
    content = [set() for _ in range(len(slots) + 1)]
    for result in result_list:
      for i in range(len(result['sp'])):
        sp = result['sp'][i]
        if len(result['token'][sp[0]:sp[1]]) > 0:
          content[i].add(' '.join(result['token'][sp[0]:sp[1]]))
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
        'value': i2s[slots[i]][2:].split('.')[-1],
        'slot': i2s[slots[i]][2:],
        'dropout': 0.0
      })
      nodes.append({
        'type': 'content',
        'value': ' | '.join(list(content[i+1])),
        'dropout': dropout[i+1] / len(result_list)
      })
    rules.append(rule)
  return matched, rules

entitylist = [
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabcac4952fe3de5c00c7",
        "name": "aircraft_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabd2c4952fe3de5c00c8",
        "name": "airline_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabdec4952fe3de5c00c9",
        "name": "airline_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabe7c4952fe3de5c00ca",
        "name": "airport_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabefc4952fe3de5c00cb",
        "name": "airport_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dabf9c4952fe3de5c00cc",
        "name": "city_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac04c4952fe3de5c00cd",
        "name": "class_type"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac0dc4952fe3de5c00ce",
        "name": "connect"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac15c4952fe3de5c00cf",
        "name": "cost_relative"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac1dc4952fe3de5c00d0",
        "name": "country_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac2bc4952fe3de5c00d1",
        "name": "date_relative"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac35c4952fe3de5c00d2",
        "name": "day_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac46c4952fe3de5c00d3",
        "name": "day_number"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac4fc4952fe3de5c00d4",
        "name": "days_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac57c4952fe3de5c00d5",
        "name": "economy"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac5ec4952fe3de5c00d6",
        "name": "end_time"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac67c4952fe3de5c00d7",
        "name": "fare_amount"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac72c4952fe3de5c00d8",
        "name": "fare_basis_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac7ac4952fe3de5c00d9",
        "name": "flight_days"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac83c4952fe3de5c00da",
        "name": "flight_mod"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac8cc4952fe3de5c00db",
        "name": "flight_number"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac94c4952fe3de5c00dc",
        "name": "flight_stop"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dac9dc4952fe3de5c00dd",
        "name": "flight_time"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dacb7c4952fe3de5c00de",
        "name": "meal"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3daccac4952fe3de5c00df",
        "name": "meal_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dacd2c4952fe3de5c00e0",
        "name": "meal_description"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dacdac4952fe3de5c00e1",
        "name": "mod"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dace3c4952fe3de5c00e2",
        "name": "month_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3daceac4952fe3de5c00e3",
        "name": "or"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dacf2c4952fe3de5c00e4",
        "name": "period_mod"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dacfac4952fe3de5c00e5",
        "name": "period_of_day"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad02c4952fe3de5c00e6",
        "name": "restriction_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad0bc4952fe3de5c00e7",
        "name": "round_trip"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad13c4952fe3de5c00e8",
        "name": "start_time"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad1ac4952fe3de5c00e9",
        "name": "state_code"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad22c4952fe3de5c00ea",
        "name": "state_name"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad29c4952fe3de5c00eb",
        "name": "time"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad30c4952fe3de5c00ec",
        "name": "time_relative"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad3ac4952fe3de5c00ed",
        "name": "today_relative"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad42c4952fe3de5c00ee",
        "name": "transport_type"
    },
    {
        "agent_id": "5c3da6d8c4952fe3de5c009a",
        "description": "",
        "id": "5c3dad4ac4952fe3de5c00ef",
        "name": "year"
    }
]
entitymap = {}
for item in entitylist:
  entitymap[item['name']] = item['id']

def make_package(
  entitymap,
  rules,
  name='quantity',
  weight=0.01):
  import json
  package = {
    'name': name,
    'tree': {
      'intent': name,
      'type': 'intent',
      'weight': weight,
      'children': [
        {
          "type": "holder"
        }
      ]
    }
  }
  children = package['tree']['children']
  for rule in rules:
    child = {
      'type': 'order',
      'name': rule['name'],
      'dropout': 0,
      'children': []
    }
    children.append(child)
    nodes = child['children']
    for node in rule['nodes']:
      if node['dropout'] < 1.0:
        if node['type'] == 'content':
          content = node['value'].split(' | ')
          nodes.append({
            'content': content,
            'type': 'content',
            'cut': 0,
            'name': content[0],
            'dropout': node['dropout']
          })
        elif node['type'] == 'entity':
          nodes.append({
            'type': 'content',
            'cut': 0,
            'isSlot': True,
            'name': '<%s>' % node['value'],
            'entity': entitymap[node['value']],
            'slot': node['slot']
          })
  return json.dumps(package)

# matched, rules = auto_rules(lambda x: 'flight' == i2in[x])
# print('matched: ', matched)

# with open('package-flight.txt', 'w', encoding='utf-8') as fout:
#   fout.write(make_package(
#     entitymap,
#     rules,
#     name='flight',
#     weight=0.73))

if __name__ == "__main__":
  # STAT_DIR = 'data/stats'
  # gen_querys(train_ds, os.path.join(STAT_DIR, 'train_query.txt'))
  # gen_querys(test_ds, os.path.join(STAT_DIR, 'test_query.txt'))
  # gen_slots(train_ds, 'data/entities')
  gen_dataset(test_ds, 'data/test.txt')
  gen_dataset(train_ds, 'data/train.txt')
  pass
