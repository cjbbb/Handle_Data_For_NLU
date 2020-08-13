import json
import copy
import random


def gen_from_file(name, in_path='./data/data_2170/train.txt', is_test=False):
    file_name = in_path.split('/')[-1].split('.')[0]
    f = open(in_path, 'r', encoding='utf8')
    datas = [eval(line[:-1]) for line in f.readlines()]
    f.close()
    # print(datas[0])

    # generate intent detection dataset
    gen_intent_detection(datas, name, file_name, is_test)

    # generate slot filling dataset
    gen_slot_filling(datas, name, file_name, is_test)

    print('done!')


def gen_intent_detection(datas, name, file_name, is_test):
    intent = {}
    i = 0
    if not is_test:
        out_path = './data/intent_detection/' + name + '_' + file_name + '.tsv'
        f_out = open(out_path, 'w', encoding='utf8')
        f_out.write('label\tbody\n')
        for item in datas:
            if item['intent'] not in intent.keys():
                intent[item['intent']] = i
                i += 1
            f_out.write(str(intent[item['intent']]) + '\t' + item['query'] + '\n')
        f_out.close()
    else:
        test_path = './data/intent_detection/' + name + '_test.tsv'
        dev_path = './data/intent_detection/' + name + '_dev.tsv'
        f_test = open(test_path, 'w', encoding='utf8')
        f_dev = open(dev_path, 'w', encoding='utf8')
        f_test.write('label\tbody\n')
        f_dev.write('label\tbody\n')
        for item in datas[:int(len(datas)/2)]:
            if item['intent'] not in intent.keys():
                intent[item['intent']] = i
                i += 1
            f_test.write(str(intent[item['intent']]) + '\t' + item['query'] + '\n')
        for item in datas[int(len(datas)/2):]:
            if item['intent'] not in intent.keys():
                intent[item['intent']] = i
                i += 1
            f_dev.write(str(intent[item['intent']]) + '\t' + item['query'] + '\n')
        f_test.close()
        f_dev.close()
    with open('./data/intent_detection/' + name + '_' + file_name + '.json', 'w') as f:
        json.dump(intent, f)
    print(intent)


def gen_slot_filling(datas, name, file_name, is_test):
    if not is_test:
        out_path = './data/slot_filling/' + name + '_' + file_name + '.dat'
        f_out = open(out_path, 'w', encoding='utf8')
        check_slot(datas, f_out)
        f_out.write('-DOCSTART- -X- O O')
        f_out.close()
    else:
        test_path = './data/slot_filling/' + name + '_test.dat'
        dev_path = './data/slot_filling/' + name + '_dev.dat'
        f_test = open(test_path, 'w', encoding='utf8')
        f_dev = open(dev_path, 'w', encoding='utf8')
        check_slot(datas[:int(len(datas) / 2)], f_test)
        check_slot(datas[int(len(datas)/2):], f_dev)
        f_test.write('-DOCSTART- -X- O O')
        f_dev.write('-DOCSTART- -X- O O')
        f_test.close()
        f_dev.close()


def check_slot(datas, f):
    for item in datas:
        words = item['query'].split()
        slots = {}
        for slot in item['slots']:
            for i, w in enumerate(slot[1].split()):
                slot_name = copy.deepcopy(slot[0].split('.')[-1]).upper()
                if slot_name != 'O':
                    slot_name = 'B-' + slot_name if not i else 'I-' + slot_name
                slots[w] = slot_name

        # i = 0
        for word in words:
            if word in slots.keys():
                f.write(word + '\t' + slots[word] + '\n')
            else:
                f.write(word + '\tO\n')
            # if word == item['query_slot']['token'][i]:
            #     f.write(word + '\tO\n')
            #     i += 1
            # elif i + 1 < len(item['query_slot']['token']) and word == item['query_slot']['token'][i + 1]:
            #     f.write(word + '\tO\n')
            #     i += 2
            # else:
            #     f.write(word + '\t' + item['query_slot']['token'][i] + '\n')
        f.write('\n')
        # try:
        #     assert i >= len(item['query_slot']['token']) - 1
        # except AssertionError:
        #     print(item)


def gen_shuffle_data(in_path, out_path, num):
    fin = open(in_path, 'r', encoding='utf8')
    fout = open(out_path, 'w', encoding='utf8')
    lines = fin.readlines()
    random.shuffle(lines)
    for line in lines[:3570]:
        fout.write(line)
        #print(line)
    fin.close()
    fout.close()


if __name__ == '__main__':
    # gen_shuffle_data('data/data_4979/test.txt', 'data/data_2170/test.txt', 2170)
    gen_from_file('atis')
