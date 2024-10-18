# -*- encoding:utf-8 -*-

import os
from entity import ruler
from trag_tree import EntityTree
import csv


print('Now run main.py.')


# 读取数据集，并将数据加入nlp中

rel = []

# print(process.process_document(nlp, 'Global Service Centre in Budapest is under UNHCR Innovation Service'))
#
# print('--------test Babelscape/rebel-large is over--------')

entities_list = set()

with open('entities_file.csv', "r", encoding='utf-8') as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        rel.append({'subject': row[0].strip(), 'object': row[1].strip()})
        entities_list.add(row[0].strip())
        entities_list.add(row[1].strip())


with open('entities.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    for ent in entities_list:
        writer.writerows([[ent]])


nlp = ruler.enhance_spacy(list(entities_list))

# 根据数据集构造出EntityTree和forest
data = []
root_list = set()
out_degree = set()
forest = []

for dependency in rel:
    print(dependency)
    data.append([dependency['subject'].lower().strip(), dependency['object'].lower().strip()])
    out_degree.add(dependency['subject'].lower().strip())

for edge in data:
    if edge[1] not in out_degree:
        root_list.add(edge[1])

print()
success_cnt = 0
for root in root_list:
    print(f"构建根节点为{root}的树")
    new_tree = EntityTree(root, data)
    if new_tree.root is None:
        print("build tree failed")
        exit(-1)
    else:
        print(f"build tree success: {new_tree}")
        success_cnt += 1
        print(f'已经构建了{success_cnt}棵树')
    if success_cnt > 30:
        break
    forest.append(new_tree)
print()

for test_tree in forest:
    test_tree.print_tree()

test_tree = forest[0]

# 测试EntityTree三种方式的搜索效果
print('测试EntityTree三种方式的搜索效果')
print(f"entity: 'high commissioner executive office', bfs_search result  : {test_tree.bfs_search('外科')}")
print(f"entity: 'high commissioner executive office', bfs_search2 result : {test_tree.bfs_search2('外科')}")
print(f"entity: 'high commissioner executive office', layer_search result: {test_tree.layer_search('外科')}")

print()
print(f"entity: 'deputy high commissioner', bfs_search result  : {test_tree.bfs_search('妇联')}")
print(f"entity: 'deputy high commissioner', bfs_search2 result : {test_tree.bfs_search2('妇联')}")
print(f"entity: 'deputy high commissioner', layer_search result: {test_tree.layer_search('妇联')}")

print()
print(f"entity: 'assistant high commissioner for operations', bfs_search result  : {test_tree.bfs_search('医院')}")
print(f"entity: 'assistant high commissioner for operations', bfs_search2 result : {test_tree.bfs_search2('医院')}")
print(f"entity: 'assistant high commissioner for operations', layer_search result: {test_tree.layer_search('医院')}")


# 测试祖先、子节点的查找效果
sentence = "医院"
result_cat = test_tree.bfs_search(sentence)
if result_cat is not None:
    print()
    print(f"entity: {sentence}, ancestors: {str([c.get_entity() for c in result_cat.get_ancestors()])}, children: {str([c.get_entity() for c in result_cat.get_children()])}")

sentence = "unhcr innovation service"
result_cat = test_tree.bfs_search(sentence)
if result_cat is not None:
    print(f"entity: {sentence}, ancestors: {str([c.get_entity() for c in result_cat.get_ancestors()])}, children: {str([c.get_entity() for c in result_cat.get_children()])}")


# 测试nlp的解析效果、EntityTree的搜索效果、上下文的构建效果
sentence = '克雷菲尔德市立医院助产士和手术室护士在医院，放眼未来，我有着好的价值观念和白内障'
print("测试nlp解析效果："+sentence)

search_result = ruler.search_entity_info(forest[0], nlp, sentence)
print()
print(search_result)
print(f"bfs_search entities: {str([c.get_entity() for c in search_result if c is not None])}")
print(f"bfs_search contexts: {str([c.get_context() for c in search_result if c is not None])}")

search_result = ruler.search_entity_info(forest[0], nlp, sentence, method=2)
print()
print(search_result)
print(f"bfs_search2 entities: {str([c.get_entity() for c in search_result if c is not None])}")
print(f"bfs_search2 contexts: {str([c.get_context() for c in search_result if c is not None])}")

search_result = ruler.search_entity_info(forest[0], nlp, sentence, method=3)
print()
print(search_result)
print(f"layer_search entities: {str([c.get_entity() for c in search_result if c is not None])}")
print(f"layer_search contexts: {str([c.get_context() for c in search_result if c is not None])}")
