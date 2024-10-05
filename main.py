import spacy
from entity import relation, ruler
from trag_tree import EntityTree
import csv

nlp = ruler.get_enhanced_nlp()

rel = []

with open('entities_file.csv', "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',')
    for row in csvreader:
        rel.append({'subject': row[0], 'object': row[1]})

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

for root in root_list:
    new_tree = EntityTree(root, data)
    forest.append(new_tree)

for test_tree in forest:
    test_tree.print_tree()
    print(test_tree.bfs_search('high commissioner executive office'))
    print(test_tree.bfs_search('deputy high commissioner'))
    print(test_tree.bfs_search('assistant high commissioner for operations'))
    result_cat = test_tree.bfs_search('deputy high commissioner')
    if result_cat is not None:
        print('find cat: father is '+result_cat.get_parent().get_entity()
              +", children is "+str([c.get_entity() for c in result_cat.get_children()] ))

sentence = 'i love deputy high commissioner'
search_result = ruler.search_entity_info(forest[0], nlp, sentence)
print(str([c.get_entity() for c in search_result]))
