import json
import codecs


def _output_result(node, level, tag):
    content = []
    if 'text' in node:
        if level == Output.SENTENCE_LEVEL:
            content.append(node['text'])
        else:
            token = node['text']
            if level == Output.WORD_LEVEL:
                token = token.split()
            for text in zip(list(token), tag(len(token), node.get('entity'))):
                # print( node.get('entity'))
                content.append('%s\t%s,' % text)
               # print('%s\t%s' % text)
    if 'children' in node:
        for child in node['children']:
            if level == Output.CHAR_LEVEL and len(content):
                content.append(' \tO,')
            content.extend(_output_result(child, level, tag))
    # print(content)
    return content


def output(result, level, tag, fout):
    '''
    调试级: 'json'
    字符级: '%char\t%eneity\n'
    词级: '%word\t%entity\n'
    句级: '%intent\t%sentence'
    '''
    if level == Output.DEBUG_LEVEL:
        fout.write(json.dumps(result, ensure_ascii=False))
    else:
        content = _output_result(result, level, tag)
        #  print(content)
        if level == Output.SENTENCE_LEVEL:
            fout.write(result['children'][0]['intent'])
            fout.write('\t')
            fout.write(' '.join(content))
           # print(' '.join(content))
        else:
            for item in content:
                fout.write(item)
    fout.write('\n')


class Output(object):
    DEBUG_LEVEL = 1
    CHAR_LEVEL = 2
    WORD_LEVEL = 3
    SENTENCE_LEVEL = 4

    def __init__(self, root, entity_map):
        self.__root = root
        self.__entity_map = entity_map
        self.__outputs = []

    def addOutput(self, level, filename, tag):
        self.__outputs.append((level, filename, tag))

    def generate(self, num=None):
        if num is None:
            result = self.__root.generate(self.__entity_map)
            for item in self.__outputs:
                with codecs.open(item[1], 'a', 'utf-8') as fout:
                    output(result, item[0], item[2], fout)
        else:
            file_list = []
            for item in self.__outputs:
                file_list.append(codecs.open(item[1], 'w', 'utf-8'))
            for _ in range(num):
                result = self.__root.generate(self.__entity_map)
                for item in zip(self.__outputs, file_list):
                    output(result, item[0][0], item[0][2], item[1])
                    # print(item[0][0])
                    item[1].flush()
            for item in file_list:
                item.close()
