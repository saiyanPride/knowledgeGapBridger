import utils.constants as CONSTANTS
# logging and notifications
def info(msg): 
    print("[INFO] " + msg)

def warn(msg): 
    print("[WARN] " + msg)

def log_query_result_snippets(snippets, links):
    with open(CONSTANTS.QUERY_RESULT_LOG_FILE_PATH,'w') as tempLogFile:
        for snippet, link in zip(snippets, links):
            tempLogFile.write(snippet + " -> " + link + "\n\n")

def log_query_result_summaries(nuggets):
    with open(CONSTANTS.SNIPPET_SUMMARY_LOG_FILE_PATH,'w') as summaryFile:
        for nugget in nuggets:
            summaryFile.write(nugget+"\n")


# Natural language processing
def get_verb_Inflections(verb):
    #TODO: lemmatise `verb` if not lemmatised by the user, if user provides lemma, then less likely to run into incorrect lemmatisation issues e.g. 'hating' -> 'hat', instead of hate
    inflections = []
    tokenised_word = CONSTANTS.nlp(verb)[0]

    for pos_tag in CONSTANTS.PENN_TREEBANK_POS_TAGS_VERBS:
        inflections.append ( tokenised_word._.inflect(pos_tag) )

    return inflections if len(inflections) > 0 else [verb]

def get_enriched_context_string(context_list):
    #TODO: use NLP to enrich `context_list`, this helps with automating the crafting of queries to fit context
    # ['electric','electricity'] should be enriched to give the final result 'electric electricity electronic current'
    return ' '.join(context_list)

def is_noun_or_noun_phrase(word):
    token = CONSTANTS.nlp(word)[0]
    result = True if token.tag_ in CONSTANTS.PENN_TREEBANK_POS_TAGS_NOUNS else False
    return result

def get_lemma(word):
    return CONSTANTS.nlp(word)[0].lemma_