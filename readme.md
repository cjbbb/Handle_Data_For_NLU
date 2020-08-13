FixNewData.py：处理得到的原始数据集中test文件夹下数据结尾是' \n'而不是'\n'的问题

gen_dataset.py: 自带的，没有使用到。

gen_entity.py: 自带的，用来给atis数据集生成entitise

gen_packages.py: 魔改的，用来给atis数据集生成packages，方便放到https://wzyjerry.github.io/interactive-syntax-tree上来观看树形图。

genDataTree.py: 魔改的，用来生成最后用来生成数据的树，是所有intent生成的树的汇总，结果为TreeSum.json

genNewDataPackages.py：用来给新的数据集生成packages,

genNewDataTree.py：用来给新的数据集生成汇总的树

handle_test.py:处理atis用的。将合并的数据集test，分成test和valid形式

handleNewData.py: 处理新的数据集。用来生成适应以前架构的，train列表和Entity集合。

stats.py/split_train.py: 未处理，是以前原有的代码





