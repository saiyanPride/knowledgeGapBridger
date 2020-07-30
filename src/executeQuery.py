from assimilation.queryResultAnalyser import summarise_snippet, summarise_snippet_by_getting_noun_chunks
from searchEngine.searchEngines import queryGoogle, querySearchEngine
from utils.helperFunctions import info, warn, log_query_result_snippets, log_query_result_summaries,get_verb_Inflections, get_enriched_context_string
import utils.constants as CONSTANTS
import json
import pyinflect

def extract_query_keywords(exact_query_terms):
    """
    returns a set of the keywords in `exact_query_terms`
    """
    keywords = []
    exact_query_terms = [term.lower() for term in exact_query_terms] # query terms are typically not longer than a sentence, so performance hit not too bad
    
    for term in exact_query_terms:
        keywords += term.split() # some terms in the query consist of multiple words, the indivdual words are desired
    
    return set(keywords)

def get_nuggets_ordered_by_proximity_to_keywords(snippets, urls, keywords_set):
    """
    returns a list of tuples, where each tuple contains a nugget and its smallest distance to a keyword i.e. (nugget, distance)
    """
    nugget_distance_pairs = [] 
    for snippet, url in zip(snippets, urls):
        nugget_distance_pairs += summarise_snippet(snippet, keywords_set)
        # TODO: consider including the url in the result
    nugget_distance_pairs.sort(key=lambda item: item[1])
    return nugget_distance_pairs

def deduplicate_nuggets_stable(nugget_distance_pairs):
    """
    remove nuggets that are the same and maintain order of occurence in `nugget_distance_pairs`
    """
    seen_nuggets = set()
    deduplicated_nuggets =[]
    for nugget_distance_pair in nugget_distance_pairs:
        if nugget_distance_pair[0] not in seen_nuggets:
            seen_nuggets.add(nugget_distance_pair[0])
            deduplicated_nuggets.append(nugget_distance_pair)
    
    return deduplicated_nuggets

def generate_snippet_summaries(snippets, urls, exact_query_terms):
    keywords_set = extract_query_keywords(exact_query_terms)
    
    # merge snippet summaries into single list
    nugget_distance_pairs = get_nuggets_ordered_by_proximity_to_keywords(snippets, urls, keywords_set)
    nugget_distance_pairs = deduplicate_nuggets_stable(nugget_distance_pairs)
    #TODO: order the results by relevance
        #nuggets like "I, "you" can be considered irrelevant, whilst for other terms, you need a technique to find their degree of association
        # to the query terms e.g. ultrasonic is more closely related to {dog,barking,stop}, than solar panel is.
        # as a human, I know this intuitively, the challenge is now to get a computer to deduce in a computationally efficient way
        # my idea is to give each term a relevance score, and if score is too low, drop it, otherwise retain

    #TODO: remove duplicates, not just verbatim duplicates

    log_query_result_summaries(nugget_distance_pairs)

def craft_queries(verb, noun):
    verb_inflections = get_verb_Inflections(verb)
    #TODO: include synonyms in the `exact_query_terms`, but only those correlated with the context, in the UI give the user the freedom to reject some terms e.g. synonyms of emit include [produce, give off, secrete] in the context of visible light
    # for each inflection generate exact query term
    exact_query_terms = []
    for verb_inflection in verb_inflections:
        exact_query_terms.append(verb_inflection + " " + noun)
    return exact_query_terms

def traitSearch(trait, context_list, excludeTerms = None):
    """
    `trait`: describes a property of the sought object using a verb (lemmatised ideally) & noun e.g. ["emit, light"] or ['store','charge']
    `context_list`: describes the context for this search to aid ambiguity resolution e.g. ['electric','electricity'], since electric could be taken to mean thrilling excitement, electricity leans engine towards electronics
    `excludeTerms`: space separated terms to exlude e.g. ['laser', 'theatre', 'festival']
    """
    info(f"searching for results with the trait: {trait[0]} {trait[1]}")
    assert( len(trait) == 2) #TODO: replace with exception handler which verifies that first word is a verb & second is a noun
    
    verb = trait[0]
    noun = trait[1]
    exact_query_terms = craft_queries(verb, noun)
    
    # enrich context of the search with other strongly correlated & relevant terms
    context_string = get_enriched_context_string(context_list) 
    
    snippets = []
    urls = []
    #TODO: cap the number of searches, to avoid the possibility of an infinite search
    for exact_query_term in exact_query_terms:
        snippets_, urls_ = querySearchEngine(CONSTANTS.GOOGLE_ENGINE, exact_query_term, context_string, excludeTerms)
        snippets += snippets_
        urls += urls_
    
    log_query_result_snippets(snippets, urls)
    generate_snippet_summaries(snippets, urls, exact_query_terms)    
    info(" Trait search is complete")

def test():
    # sample trait search
    traitSearch(['stop', 'dog barking'], ['noise', 'neighbour'])
    #traitSearch(['absorb', 'shock'], ['material', 'compressible'])
    #traitSearch(['withstands', 'strain'], ['material','property'], 'rubber cutting')
    #traitSearch(['emit', 'visible light'], ['wavelength'])
    #traitSearch(['convert', 'binary to image'], ['memory cells','circuit','data', 'store'])
    #traitSearch(['price', 'poison pill'], ['model', 'technique'], ['drug','drugs'])

"""
def usage():
    query_list = ['stores', 'electric', 'charge']
    context_string = '' #helps to filter
    query_pos_list = ['' for term in query_list]
    query_pos_list[0] = [CONSTANTS.VERB]   # 'v' for verb
                                                # engine will try to infer, but user can specify
                                                # let's the engine know that the verb homograph (same spelling, diff meaning, only synonyms have same meaning) should be used

    should_use_inflections = [False for term in query_list]
    #should_use_inflections[0] = True # queries using inflections of 'stores' such as stored, storing, store should be generated
                                    # note that google search is smart enough to include inflections in results
    exact_terms = []
    exclude_terms = []
    or_search_terms = [] # this is used to filter results from other search paramters, at least one of these must be in results
    
    smartQuery(query_list, context_string, query_pos_list)
"""

if __name__ == '__main__':
    test()