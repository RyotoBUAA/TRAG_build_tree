import spacy
from entity import ruler
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import torch


relation_pattern = ['parent organization',
                    'office held by head of the organization',
                    'part of'
                    ]


# 文档预处理
def preprocess_text(nlp, document):
    doc = nlp(document)
    sentences = [sent.text for sent in doc.sents]
    result = []
    for sentence in sentences:
        doc = nlp(sentence)
        for ind1, ent1 in enumerate(doc.ents):
            for ind2, ent2 in enumerate(doc.ents):
                if ind2 > ind1 and ent1.label_ == 'EXTRA' and ent2.label_ == 'EXTRA':
                    candidate_text = sentence
                    candidate_text = candidate_text.replace(ent1.text, f"\"{ent1.text}\"")
                    candidate_text = candidate_text.replace(ent2.text, f"\"{ent2.text}\"")
                    result.append(candidate_text)

    return result


triplet_extractor = pipeline('text2text-generation', model='Babelscape/rebel-large', tokenizer='Babelscape/rebel-large', device='cuda:0')


def extract_triplets(input_text):
    text = triplet_extractor.tokenizer.batch_decode(
        [triplet_extractor(input_text, return_tensors=True, return_text=False)[0]["generated_token_ids"]])[0]

    triplets = []
    relation, subject, relation, object_ = '', '', '', ''
    text = text.strip()
    current = 'x'
    for token in text.replace("<s>", "").replace("<pad>", "").replace("</s>", "").split():
        if token == "<triplet>":
            current = 't'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
                relation = ''
            subject = ''
        elif token == "<subj>":
            current = 's'
            if relation != '':
                triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})
            object_ = ''
        elif token == "<obj>":
            current = 'o'
            relation = ''
        else:
            if current == 't':
                subject += ' ' + token
            elif current == 's':
                object_ += ' ' + token
            elif current == 'o':
                relation += ' ' + token
    if subject != '' and relation != '' and object_ != '':
        triplets.append({'head': subject.strip(), 'type': relation.strip(), 'tail': object_.strip()})

    return triplets


def process_document(nlp, document):
    # 文档预处理
    preprocessed_sentences = preprocess_text(nlp, document)

    relations = []

    # 实体识别与关系提取
    # entities, relations = extract_entities_and_relations(nlp, preprocessed_sentences)
    for sentence in preprocessed_sentences:
        print("input sentence: "+sentence)
        triplets = extract_triplets(sentence)
        for triplet in triplets:
            print(" * this sentence has a relation: "+str(triplet))
            if triplet['type'] in relation_pattern:
                relations.append({'subject': triplet['head'], 'object': triplet['tail']})
        print("")
        print("")
    return relations
