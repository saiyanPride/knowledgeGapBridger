from privateEnvVariables import API_KEY, CUSTOM_SEARCH_ENGINE_ID
from googleapiclient.discovery import build
from queryResults.queryResultAnalyser import summarise_snippet, summarise_snippet_get_noun_chunks
import json
import spacy
import pyinflect

VERB = 'v'
NUM_RESULTS_PER_QUERY = 10
LANGUAGE = 'lang_en'
GOOGLE_SEARCH_API_SERVICE_NAME = "customsearch"
GOOGLE_SEARCH_API_VERSION = "v1"
GOOGLE = "GOOGLE"

# NLP
nlp = spacy.load('en_core_web_sm')
PENN_TREEBANK_POS_TAGS_VERBS = ('VB', 'VBD', 'VBG', 'VBN','VBP','VBZ')

# FILE PATHS
QUERY_RESULT_LOG_FILE_PATH = 'logs/queryResults.txt'
SNIPPET_SUMMARY_LOG_FILE_PATH = 'logs/snippetSummaries.txt'

def info(msg): print("[INFO] " + msg)
def warn(msg): print("[WARN] " + msg)

def queryGoogle(query, exact_terms, or_terms, exclude_terms):
    info("running a google query")
    query_service = build(GOOGLE_SEARCH_API_SERVICE_NAME, GOOGLE_SEARCH_API_VERSION, developerKey=API_KEY) #this engine lacks intelligence features

    query_response = query_service.cse().list(q=query, cx=CUSTOM_SEARCH_ENGINE_ID, exactTerms=exact_terms, 
                                                orTerms=or_terms, excludeTerms=exclude_terms,lr=LANGUAGE).execute() 
    
    # extract results
    result_urls = []
    result_snippets = []
    
    try:
        for result_item in query_response['items']:
            result_urls.append(result_item['link'])
            result_snippets.append(result_item['snippet'])
    except: #TODO: improve this error handle, note down the issue
        pass

    return (result_snippets, result_urls)

def querySearchEngine(search_engine, exact_query_term, context_string, excludeTerms):
    #see https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list for parameter definitions
    # will add more search engines in the future
    if(search_engine == GOOGLE): 
        return queryGoogle("", exact_query_term, context_string, excludeTerms)
    else: # default
        return queryGoogle("", exact_query_term, context_string, excludeTerms)

def getVerbInflections(verb):
    #TODO: lemmatise `verb` if not lemmatised by the user, if user provides lemma, then less likely to run into incorrect lemmatisation issues e.g. 'hating' -> 'hat', instead of hate
    inflections = []
    tokenised_word = nlp(verb)[0]

    for pos_tag in PENN_TREEBANK_POS_TAGS_VERBS:
        inflections.append ( tokenised_word._.inflect(pos_tag) )

    return inflections if len(inflections) > 0 else [verb]

def get_enriched_context_string(context_list):
    #TODO: use NLP to enrich `context_list`, this helps with automating the crafting of queries to fit context
    # ['electric','electricity'] should be enriched to give the final result 'electric electricity electronic current'
    return ' '.join(context_list)

def logTempResults(snippets, links):
    with open(QUERY_RESULT_LOG_FILE_PATH,'w') as tempLogFile:
        for snippet, link in zip(snippets, links):
            tempLogFile.write(snippet + " -> " + link + "\n\n")

def generate_snippet_summaries(snippets, urls, exact_query_terms):
    keywords = []
    
    exact_query_terms = [term.lower() for term in exact_query_terms] # query terms are typically not longer than a sentence, so performance hit not too bad

    for term in exact_query_terms:
        keywords += term.split() # some terms in the query consist of multiple words, the indivdual words are desired
    
    keywords_set = set(keywords)
    
    # merge snippet summaries into single list
    nuggets = [] 
    for snippet, url in zip(snippets, urls):
        nuggets += summarise_snippet_get_noun_chunks(snippet, keywords_set)
        nuggets += summarise_snippet(snippet, keywords_set)
        #nuggets.append(f"url->{url}]") # if you want url info, see the queryResults
    
    nuggets = set(nuggets) # this just removes verbatim duplicates

    #TODO: order the results by relevance
        #nuggets like "I, "you" can be considered irrelevant, whilst for other terms, you need a technique to find their degree of association
        # to the query terms e.g. ultrasonic is more closely related to {dog,barking,stop}, than solar panel is.
        # as a human, I know this intuitively, the challenge is now to get a computer to deduce in a computationally efficient way
        # my idea is to give each term a relevance score, and if score is too low, drop it, otherwise retain

    #TODO: remove duplicates, not just verbatim duplicates

    # write snippet summaries to file
    with open(SNIPPET_SUMMARY_LOG_FILE_PATH,'w') as summaryFile:
        for nugget in nuggets:
            summaryFile.write(nugget+"\n")

def traitSearch(trait, context_list, excludeTerms = None):
    """
    `trait`: describes a property of the sought object using verb (lemmatised ideally) & noun e.g. ["emit, light"] or ['store','charge']
    `context_list`: describes the context for this search to avoid ambiguity e.g. ['electric','electricity'], since electric could be taken to mean thrilling excitement
    `excludeTerms`: space separated terms to exlude e.g. ['laser', 'theatre', 'festival']
    """
    info(f"searching for objects with the trait: {trait[0]} {trait[1]}")
    #TODO: validate `trait` assert( len(trait) == 2) & that first term is verb and second term is noun
    verb = trait[0]
    noun = trait[1]

    verb_inflections = getVerbInflections(verb)
    # for each inflection generate exact query term
    exact_query_terms = []
    for verb_inflection in verb_inflections:
        exact_query_terms.append(verb_inflection + " " + noun)
    
    #TODO: include synonyms in the `exact_query_terms`, but only those correlated with the context, in the UI give the user the freedom to reject some terms e.g. synonyms of emit include [produce, give off, secrete] in the context of visible light

    # enrich context of the search with other strongly correlated & relevant terms
    context_string = get_enriched_context_string(context_list) 
    
    snippets = []
    urls = []
    #TODO: cap the number of searches, to avoid the possibility of an infinite search
    for exact_query_term in exact_query_terms:
        snippets_, urls_ = querySearchEngine(GOOGLE, exact_query_term, context_string, excludeTerms)
        snippets += snippets_
        urls += urls_
    
    logTempResults(snippets, urls)
    generate_snippet_summaries(snippets, urls, exact_query_terms)    
    info(" trait search complete")

def test():

    # sample trait search
    traitSearch(['stop', 'dog barking'], ['noise', 'neighbour'])
    #traitSearch(['absorb', 'shock'], ['material', 'compressible'])
    #traitSearch(['withstands', 'strain'], ['material','property'], 'rubber cutting')
    #traitSearch(['emit', 'visible light'], ['wavelength'])
    #traitSearch(['convert', 'binary to image'], ['memory cells','circuit','data', 'store'])
    #traitSearch(['price', 'poison pill'], ['model', 'technique'], ['drug','drugs'])

    # sample word inflection
    """
    nlp = spacy.load('en_core_web_sm')
    word = 'emits'
    tokens = nlp(word)
    tokenised_word = tokens[0]

    inflection_pos_tags = ['VB', 'VBD', 'VBG', 'VBN','VBP','VBZ']

    for pos_tag in inflection_pos_tags:
        inflection = tokenised_word._.inflect(pos_tag)
        print(f"inflection of {word} in form {pos_tag} is {inflection}")
    """

def usage():
    query_list = ['stores', 'electric', 'charge']
    context_string = '' #helps to filter
    query_pos_list = ['' for term in query_list]
    query_pos_list[0] = [VERB]   # 'v' for verb
                                                # engine will try to infer, but user can specify
                                                # let's the engine know that the verb homograph (same spelling, diff meaning, only synonyms have same meaning) should be used

    should_use_inflections = [False for term in query_list]
    #should_use_inflections[0] = True # queries using inflections of 'stores' such as stored, storing, store should be generated
                                    # note that google search is smart enough to include inflections in results
    exact_terms = []
    exclude_terms = []
    or_search_terms = [] # this is used to filter results from other search paramters, at least one of these must be in results
    
    smartQuery(query_list, context_string, query_pos_list)

if __name__ == '__main__':
    test()