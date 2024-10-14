import spacy
import csv
from spacy.pipeline import EntityRuler


def enhance_spacy(entities):
    nlp = spacy.load("zh_core_web_sm")

    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = []

    for entity in entities:
        pattern = []
        words = list(entity.lower().strip().split())
        for word in words:
            pattern.append({"LOWER": word})

        patterns.append({"label": "EXTRA", "pattern": pattern})

    ruler.add_patterns(patterns)

    return nlp


def get_enhanced_nlp():
    with open('entities.csv', "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        entities = []
        for row in csvreader:
            entities.append(row[0])
        return enhance_spacy(entities)


def search_entity_info(tree, nlp, search, method=1):
    search_context = []
    search = search.lower().strip()

    doc = nlp(search)
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            if method == 1:
                search_context.append(tree.bfs_search(ent.text))
            elif method == 2:
                search_context.append(tree.bfs_search2(ent.text))
            elif method == 3:
                search_context.append(tree.layer_search(ent.text))
            else:
                print("not supported method")
                return None

    return search_context
