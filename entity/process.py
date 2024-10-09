import spacy
from entity import ruler


# 文档预处理
def preprocess_text(nlp, document):
    doc = nlp(document)
    sentences = [sent.text for sent in doc.sents]
    return sentences


# 实体识别与关系提取
def extract_entities_and_relations(nlp, sentences):
    all_entities = []
    all_relations = []

    for sentence in sentences:
        doc = nlp(sentence)

        entities = [(ent.text, ent.label_) for ent in doc.ents]

        all_entities.extend(entities)

        # 提取关系
        relations = []
        for token in doc:
            if token.dep_ in ('nsubj', 'dobj', 'poss'):  # 简单的主语、宾语依赖关系
                relations.append((token.text, token.dep_, token.head.text))
        all_relations.extend(relations)

    return all_entities, all_relations


# 构建实体之间的从属关系
def build_entity_hierarchy(entities, relations):
    hierarchy = {}

    for entity, dep, head in relations:
        if dep == 'nsubj':  # 主语可能是实体的父节点
            if head not in hierarchy:
                hierarchy[head] = []
            hierarchy[head].append(entity)

    return hierarchy


def process_document(nlp, document):
    # 文档预处理
    preprocessed_sentences = preprocess_text(nlp, document)

    # 实体识别与关系提取
    entities, relations = extract_entities_and_relations(nlp, preprocessed_sentences)
    print(entities)
    print(relations)

    # 构建实体层次关系
    entity_hierarchy = build_entity_hierarchy(entities, relations)

    return entity_hierarchy
