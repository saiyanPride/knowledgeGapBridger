from secrets.privateEnvVariables import API_KEY, CUSTOM_SEARCH_ENGINE_ID
from googleapiclient.discovery import build
from utils.helperFunctions import info
import utils.constants

def queryGoogle(query, exact_terms, or_terms, exclude_terms):
    info("running a google query")
    query_service = build(utils.constants.GOOGLE_SEARCH_API_SERVICE_NAME, utils.constants.GOOGLE_SEARCH_API_VERSION, developerKey=API_KEY) #this engine lacks intelligence features

    query_response = query_service.cse().list(q=query, cx=CUSTOM_SEARCH_ENGINE_ID, exactTerms=exact_terms, 
                                                orTerms=or_terms, excludeTerms=exclude_terms,lr=utils.constants.LANGUAGE).execute() 
    
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
    if(search_engine == utils.constants.GOOGLE_ENGINE): 
        return queryGoogle("", exact_query_term, context_string, excludeTerms)
    else: # default
        return queryGoogle("", exact_query_term, context_string, excludeTerms)