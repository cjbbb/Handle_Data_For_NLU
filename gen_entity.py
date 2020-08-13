entities = {}

with open('data/train.txt', 'r', encoding='utf-8') as fin:
  for line in fin:
    query = eval(line)
    for p in query['slots']:
      t = p[0].split('.')[-1]
      entities.setdefault(t, set())
      entities[t].add(p[1])

for kind in entities:
  with open('data/active_entities/%s' % kind, 'w', encoding='utf-8') as fout:
    for item in entities[kind]:
      fout.write('%s\n' % item)
