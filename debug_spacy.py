import spacy

nlp = spacy.load("en_core_web_sm", disable=["parser", "tagger", "lemmatizer", "attribute_ruler", "tok2vec"])
ruler = nlp.add_pipe("entity_ruler", before="ner")
patterns = [
    {"label": "RANK", "pattern": [{"TEXT": {"REGEX": r"(?i)^tier-\d+$"}}, {"IS_TITLE": True, "OP": "?"}]},
    {"label": "RANK", "pattern": [{"LOWER": "tier"}, {"TEXT": "-"}, {"IS_DIGIT": True}, {"IS_TITLE": True, "OP": "?"}]},
    {"label": "GPE", "pattern": [{"IS_TITLE": True, "OP": "+"}, {"LOWER": "realm"}]},
]
ruler.add_patterns(patterns)

doc = nlp("He became a Tier-3 Mage after consulting the Inner Disciple. They traveled from the Upper Realm to join the Azure Cloud Sect.")

print("Tokens:")
for t in doc:
    print(f"[{t.text}] (is_title: {t.is_title}, lower: {t.lower_})")

print("\nEntities:")
for ent in doc.ents:
    print(ent.text, "->", ent.label_)
