lines = []
with open('2x/test/seq.in', 'r', encoding='utf-8') as fr1:
    while 1:
        line = fr1.readline()
        print(line.split(' '))
        if not line:
            break
        lines.append(line)
with open('2x/test/seq.in', 'w', encoding='utf-8') as fw1:
    for i in lines:
        fw1.write(i + '\n')
