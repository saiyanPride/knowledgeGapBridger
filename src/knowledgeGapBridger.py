from privateEnvVariables import API_KEY, CUSTOM_SEARCH_ENGINE_ID
from googleapiclient.discovery import build
import json
VERB = 'v'

def smartQuery(query_list, context_string='', parts_of_speech_disambiguation=None):
    
    # generate queries
    # for each query compile result
        # in the form: containing sentence, links
    queries = []

    for query in queries:
        #below should be a function call
        query_service = build("customsearch", "v1", developerKey=API_KEY) #this engine lacks intelligence features
        query_response = query_service.cse().list(q=query,
                                                cx=CUSTOM_SEARCH_ENGINE_ID,
                                                ).execute() 
        result_items = query_response['items']
        result_urls = []

        for result_item in result_items:
            result_urls.append(result_item['link'])
            print(result_item['link'])

def test():
    #api reference guide: https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list
    print("\ntesting\n")
    query_service = build("customsearch", "v1", developerKey=API_KEY) #this engine lacks intelligence features
    query = 'store electric charge'#'light'
    exact_terms = ''#"emits red light"
    exclude_terms = 'laser'
    or_terms =  ""#"electricity energy electron electric electronic"
    num_results = 10 # must be in [1,10]
    language = 'lang_en'
    query_response = query_service.cse().list(q=query,cx=CUSTOM_SEARCH_ENGINE_ID, 
                                                num = num_results, lr=language, exactTerms=exact_terms, orTerms=or_terms, excludeTerms=exclude_terms).execute() 
    
    #print( json.dumps(response, sort_keys=True, indent=4) )
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
    
    result_items = query_response['items']
    
    result_urls = []
    result_snippets = []

    for result_item in result_items:
        link = result_item['link']
        snippet = result_item['snippet']
        result_urls.append(link)
        result_snippets.append(snippet)
        print(snippet + " -> " + link + "\n")


def usage():
    query_list = ['stores', 'electric', 'charge']
    context_string = '' #helps to filter
    parts_of_speech_disambiguation = ['' for term in query_list]
    parts_of_speech_disambiguation[0] = [VERB]   # 'v' for verb
                                                # engine will try to infer, but user can specify
                                                # let's the engine know that the verb homograph (same spelling, diff meaning, only synonyms have same meaning) should be used

    should_use_inflections = [False for term in query_list]
    #should_use_inflections[0] = True # queries using inflections of 'stores' such as stored, storing, store should be generated
                                    # note that google search is smart enough to include inflections in results
    exact_terms = []
    exclude_terms = []
    or_search_terms = [] # this is used to filter results from other search paramters, at least one of these must be in results
    
    smartQuery(query_list, context_string, parts_of_speech_disambiguation)

if __name__ == '__main__':
    test()