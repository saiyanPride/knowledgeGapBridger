import spacy
nlp = spacy.load('en_core_web_sm')
PENN_TREEBANK_POS_TAGS_NOUNS = ["NN","NNP","NNS","NNPS"]
END_OF_SUMMARY_DELIMETER = ";"

def info(msg): print("[INFO] " + msg)