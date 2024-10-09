import spacy
from entity import relation, ruler, process
from trag_tree import EntityTree
import csv


# 读取数据集，并将数据加入nlp中
nlp = ruler.get_enhanced_nlp()
rel = []

print(process.process_document(nlp, 'High Commissioner Executive Office is UNHCR Innovation Service.'))

with open('entities_file.csv', "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        rel.append({'subject': row[0], 'object': row[1]})


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
for root in root_list:
    new_tree = EntityTree(root, data)
    if new_tree.root is None:
        print("build tree failed")
        exit(-1)
    else:
        print(f"build tree success: {new_tree}")
    forest.append(new_tree)
print()

test_tree = forest[0]
test_tree.print_tree()


# 测试EntityTree三种方式的搜索效果
print()
print(f"entity: 'high commissioner executive office', bfs_search result  : {test_tree.bfs_search('high commissioner executive office')}")
print(f"entity: 'high commissioner executive office', bfs_search2 result : {test_tree.bfs_search2('high commissioner executive office')}")
print(f"entity: 'high commissioner executive office', layer_search result: {test_tree.layer_search('high commissioner executive office')}")

print()
print(f"entity: 'deputy high commissioner', bfs_search result  : {test_tree.bfs_search('deputy high commissioner')}")
print(f"entity: 'deputy high commissioner', bfs_search2 result : {test_tree.bfs_search2('deputy high commissioner')}")
print(f"entity: 'deputy high commissioner', layer_search result: {test_tree.layer_search('deputy high commissioner')}")

print()
print(f"entity: 'assistant high commissioner for operations', bfs_search result  : {test_tree.bfs_search('assistant high commissioner for operations')}")
print(f"entity: 'assistant high commissioner for operations', bfs_search2 result : {test_tree.bfs_search2('assistant high commissioner for operations')}")
print(f"entity: 'assistant high commissioner for operations', layer_search result: {test_tree.layer_search('assistant high commissioner for operations')}")


# 测试祖先、子节点的查找效果
sentence = "deputy high commissioner"
result_cat = test_tree.bfs_search(sentence)
if result_cat is not None:
    print()
    print(f"entity: {sentence}, ancestors: {str([c.get_entity() for c in result_cat.get_ancestors()])}, children: {str([c.get_entity() for c in result_cat.get_children()])}")

sentence = "unhcr innovation service"
result_cat = test_tree.bfs_search(sentence)
if result_cat is not None:
    print(f"entity: {sentence}, ancestors: {str([c.get_entity() for c in result_cat.get_ancestors()])}, children: {str([c.get_entity() for c in result_cat.get_children()])}")


# 测试nlp的解析效果、EntityTree的搜索效果、上下文的构建效果
sentence = 'i love deputy high commissioner'

search_result = ruler.search_entity_info(forest[0], nlp, sentence)
print()
print(f"bfs_search entities: {str([c.get_entity() for c in search_result])}")
print(f"bfs_search contexts: {str([c.get_context() for c in search_result])}")

search_result = ruler.search_entity_info(forest[0], nlp, sentence, method=2)
print()
print(f"bfs_search2 entities: {str([c.get_entity() for c in search_result])}")
print(f"bfs_search2 contexts: {str([c.get_context() for c in search_result])}")

search_result = ruler.search_entity_info(forest[0], nlp, sentence, method=3)
print()
print(f"layer_search entities: {str([c.get_entity() for c in search_result])}")
print(f"layer_search contexts: {str([c.get_context() for c in search_result])}")
