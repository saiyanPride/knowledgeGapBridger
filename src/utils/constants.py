import spacy
# NATURAL LANGUAGE PROCESSING
nlp = spacy.load('en_core_web_sm')
PENN_TREEBANK_POS_TAGS_VERBS = ('VB', 'VBD', 'VBG', 'VBN','VBP','VBZ')
PENN_TREEBANK_POS_TAGS_NOUNS = ["NN","NNP","NNS","NNPS"]
VERB = 'v'
LANGUAGE = 'lang_en'

# SEARCH ENGINES
NUM_RESULTS_PER_QUERY = 10
GOOGLE_SEARCH_API_SERVICE_NAME = "customsearch"
GOOGLE_SEARCH_API_VERSION = "v1"
GOOGLE_ENGINE = "GOOGLE"

# FILE PATHS
QUERY_RESULT_LOG_FILE_PATH = '../logs/queryResults.txt'
SNIPPET_SUMMARY_LOG_FILE_PATH = '../logs/snippetSummaries.txt'