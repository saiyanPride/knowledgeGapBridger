from privateEnvVariables import API_KEY, CUSTOM_SEARCH_ENGINE_ID
from googleapiclient.discovery import build
import json
VERB = 'v'
NUM_RESULTS_PER_QUERY = 10
LANGUAGE = 'lang_en'
GOOGLE_SEARCH_API_SERVICE_NAME = "customsearch"
GOOGLE_SEARCH_API_VERSION = "v1"
GOOGLE = "GOOGLE"

def info(msg): print("[INFO] " + msg)

def queryGoogle(query, exact_terms, or_terms, exclude_terms):
    info("running a google query")
    query_service = build(GOOGLE_SEARCH_API_SERVICE_NAME, GOOGLE_SEARCH_API_VERSION, developerKey=API_KEY) #this engine lacks intelligence features

    query_response = query_service.cse().list(q=query, cx=CUSTOM_SEARCH_ENGINE_ID, exactTerms=exact_terms, 
                                                orTerms=or_terms, excludeTerms=exclude_terms,lr=LANGUAGE).execute() 
    
    # extract results
    result_urls = []
    result_snippets = []

    for result_item in query_response['items']:
        result_urls.append(result_item['link'])
        result_snippets.append(result_item['snippet'])

    return (result_snippets, result_urls)

def querySearchEngine(search_engine, exact_query_term, context_string, excludeTerms):
    #see https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list for parameter definitions
    # will add more search engines in the future
    if(search_engine == GOOGLE): 
        return queryGoogle("", exact_query_term, context_string, excludeTerms)
    else: # default
        return queryGoogle("", exact_query_term, context_string, excludeTerms)

def getVerbInflections(verb):
    inflections = [verb]
    #TODO: determine inflections
    return inflections

def get_enriched_context_string(context_list):
    #TODO: use NLP to enrich `context_list`, this helps automating the crafting of queries to fit context
    # ['electric','electricity'] should be enriched to giver the final result 'electric electricity electronic current'
    return ' '.join(context_list)

def traitSearch(trait, context_list, excludeTerms = None):
    """
    `trait`: describes a property of the sought object using verb & noun e.g. ["emits, light"] or ['stores','charge']
    `context_list`: describes the context for this search to avoid ambiguity e.g. ['electric','electricity'], since electric could be taken to mean thrilling excitement
    `excludeTerms`: space separated terms to exlude e.g. ['laser', 'theatre', 'festival']
    """

    #TODO: validate `trait` assert( len(trait) == 2) & that first term is verb and second term is noun
    verb = trait[0]
    noun = trait[1]

    verb_inflections = getVerbInflections(verb)
    # for each inflection generate exact query term
    exact_query_terms = []
    for verb_inflection in verb_inflections:
        exact_query_terms.append(verb_inflection + " " + noun)
    
    # enrich context of the search with other strongly correlated & relevant terms
    context_string = get_enriched_context_string(context_list) 
    
    snippets = []
    links = []
    for exact_query_term in exact_query_terms:
        snippets_, links_ = querySearchEngine(GOOGLE, exact_query_term, context_string, excludeTerms)
        snippets += snippets_
        links += links_
    
    for snippet, link in zip(snippets, links):
        print(snippet + " -> " + link + "\n")

    #TODO: use NLP to remove duplicates

    #TODO: use NLP to filter the results by relevance using query_pos_list

    # return the relevant search_results after post-processing

def test():

    # sample trait search
    traitSearch(['withstands', 'strain'], ['material','property'], 'rubber cutting')
    """
    sample response
    {
            "cacheId": "lna6nn9hkIgJ",
            "displayLink": "www.pca.state.mn.us",
            "formattedUrl": "https://www.pca.state.mn.us/featured/electric-vehicles-charge-goodwill-stores",
            "htmlFormattedUrl": "https://www.pca.state.mn.us/featured/<b>electric</b>-vehicles-<b>charge</b>-goodwill-<b>stores</b>",
            "htmlSnippet": "Aug 3, 2015 <b>...</b> Goodwill supports greener transportation by adding <b>electric</b> vehicle <b>charging</b> <br>\nstations at some of their <b>stores</b>.",
            "htmlTitle": "<b>Electric</b> vehicles <b>charge</b> at Goodwill <b>stores</b> | Minnesota Pollution ...",
            "kind": "customsearch#result",
            "link": "https://www.pca.state.mn.us/featured/electric-vehicles-charge-goodwill-stores",
            "pagemap": {
                "Item": [
                    {
                        "encoded": "Last year, sales from Goodwill stores funded employment training, job placement services, financial education, youth mentoring and more to 9.8 million people in the United States and Canada....",
                        "title": "Electric vehicles charge at Goodwill stores"
                    }
                ],
                "cse_image": [
                    {
                        "src": "https://www.pca.state.mn.us/sites/default/files/styles/open_graph_image/public/310867105bd77816115eb8beca878465_XL.jpg?itok=Kz-1k65r"
                    }
                ],
                "cse_thumbnail": [
                    {
                        "height": "169",
                        "src": "https://encrypted-tbn2.gstatic.com/images?q=tbn:ANd9GcSFCHEdVQU2VGNggSghIOlh4nal92q7wEqsIkXEQnKddhTrc8id024NvYQ",
                        "width": "299"
                    }
                ],
                "metatags": [
                    {
                        "article:modified_time": "2018-06-08T12:49:07-05:00",
                        "article:published_time": "2015-08-03T14:14:51-05:00",
                        "og:description": "Goodwill supports greener transportation by adding electric vehicle charging stations at some of their stores.",
                        "og:image": "https://www.pca.state.mn.us/sites/default/files/styles/open_graph_image/public/310867105bd77816115eb8beca878465_XL.jpg?itok=Kz-1k65r",
                        "og:site_name": "Minnesota Pollution Control Agency",
                        "og:title": "Electric vehicles charge at Goodwill stores",
                        "og:type": "article",
                        "og:updated_time": "2018-06-08T12:49:07-05:00",
                        "og:url": "https://www.pca.state.mn.us/featured/electric-vehicles-charge-goodwill-stores",
                        "twitter:card": "summary",
                        "twitter:creator": "@MnPCA",
                        "twitter:description": "Goodwill supports greener transportation by adding electric vehicle charging stations at some of their stores.",
                        "twitter:image": "https://www.pca.state.mn.us/sites/default/files/styles/medium/public/310867105bd77816115eb8beca878465_XL.jpg?itok=XJyxkw0I",
                        "twitter:title": "Electric vehicles charge at Goodwill stores",
                        "twitter:url": "https://www.pca.state.mn.us/featured/electric-vehicles-charge-goodwill-stores",
                        "viewport": "width=device-width, initial-scale=1.0"
                    }
                ]
            },
            "snippet": "Aug 3, 2015 ... Goodwill supports greener transportation by adding electric vehicle charging \nstations at some of their stores.",
            "title": "Electric vehicles charge at Goodwill stores | Minnesota Pollution ..."
        },
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