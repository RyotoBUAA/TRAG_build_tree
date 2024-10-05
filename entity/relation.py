def extract_relations(doc):

    relations = []

    for token in doc:

        if token.dep_ in {"nsubj", "attr", "conj"} and token.head.dep_ in {"ROOT", "relcl", "appos"}:
            subject = token.lemma_
            object_ = None
            relation_type = None

            for child in token.head.children:
                if child.dep_ in {"prep", "attr", "pobj"} and child != token:
                    object_ = ' '.join([desc.lemma_ for desc in child.subtree if desc.dep_ == "pobj"])
                    relation_type = token.head.text
                    break

            if subject and object_:
                relations.append({'subject': subject, 'object': object_, 'relation': relation_type})

    return relations


def extract_entities_relations(doc):
    relationships = []
    for token in doc:
        if token.lower_ == "under":
            subj = [w for w in token.lefts if w.ent_type_ == "EXTRA"]
            pobj = [w for w in token.rights if w.ent_type_ == "EXTRA"]
            if subj and pobj:
                relationships.append((subj[0].text, pobj[0].text))
    return relationships
