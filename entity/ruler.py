import spacy
import csv
from spacy.pipeline import EntityRuler


def enhance_spacy(entities):
    nlp = spacy.load("en_core_web_sm")

    ruler = nlp.add_pipe("entity_ruler", before="ner")

    patterns = []

    for entity in entities:
        patterns.append({"label": "EXTRA", "pattern": entity.lower().strip()})

    ruler.add_patterns(patterns)

    return nlp


def get_enhanced_nlp():
    with open('entities.csv', "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',')
        entities = []
        for row in csvreader:
            entities.append(row[0])
        return enhance_spacy(entities)


def search_entity_info(tree, nlp, search):
    search_context = []
    search = search.lower().strip()

    doc = nlp(search)
    for ent in doc.ents:
        if ent.label_ == 'EXTRA':
            search_context.append(tree.bfs_search(ent.text))

    return search_context
