from utils.helperFunctions import info, is_noun_or_noun_phrase, get_lemma
import utils.constants as CONSTANTS
import functools

def get_nearest_keyword_distance(cnk_start, cnk_end, keyword_indices):
    """
    keyword_indices has to be non-empty list!
    keyword_indices[i] is the index of the ith keyword within the query result snippet. 

    cnk refers to a consecutive non-keyword: it could be a single word or a collection of words(phrase) which have been deemed noteworthy, 
    thus it will be included in the summary of the snippet being processed
    
    There is an implicit assumption, that the snippet will only be a few words i.e. not billions of words, otherwise integer overflows may occur when dealing with large indices e.g. the 5 billionth word's index can't be stored in a 32 bit int
    """
    keyword_size = len(keyword_indices)
    assert(keyword_size >= 1)
    assert(cnk_start <= cnk_end)
    result = 0

    def get_nearest_right_keyword_for_enclosed_cnk(cnk_index): #nested
        """
        cnk is guaranteed to be surrounded by keywords i.e. it has a nearest left keyword
        """
        nearest_right_keyword_index = -1
        for i in range(0,keyword_size): # find index in keyword_indices corresponding to nearestRightKeyword 
            if keyword_indices[i] > cnk_index: 
                nearest_right_keyword_index = i
        assert(nearest_right_keyword_index != -1)# this assertion is redundant, it is guaranteed that the nearest_right_keyword_index was found and set
        return nearest_right_keyword_index
        

    if cnk_start == cnk_end: # cnk is a single word
        cnk_index = cnk_start
        
        if keyword_size == 1: # handle case for 1 keyword
            result = abs(keyword_indices[0]- cnk_index)
        elif cnk_index < keyword_indices[0]: # cnk is to the left of first keyword i.e. cnk...firstKeyword
            result = keyword_indices[0]- cnk_index
        elif cnk_index > keyword_indices[keyword_size-1]: # cnk is to the right of last keyword i.e. lastKeyword...cnk
            result = cnk_index - keyword_indices[keyword_size-1]
        else: # cnk enclosed by 2 keywords on either side i.e. nearestLeftKeyWord...cnk...nearestRightKeyword
            # find index of nearestRightKeyword, and use it to determine index of nearestLeftKeyWord
            nearest_right_keyword_index = get_nearest_right_keyword_for_enclosed_cnk(cnk_index)
            nearest_left_keyword_index = nearest_right_keyword_index - 1
            result = min(keyword_indices[nearest_right_keyword_index] - cnk_index, cnk_index - keyword_indices[nearest_left_keyword_index])
    else: # cnk consists of >=2 consective words i.e. cnk_start < cnk_end
        if keyword_size == 1: # the sole keyword is either to the left or right of the cnk
            result = cnk_start - keyword_indices[0] if keyword_indices[0] < cnk_start else keyword_indices[0] - cnk_end
        elif cnk_end < keyword_indices[0]: # keyword_size is guaranteed to be >=2 since if this line reached i.e. we have this snippet general form 
                                            # ...firstKeyword...lastKeyWord...), so handle cases where is cnk located in each of the 3 regions (...)
            result = keyword_indices[0] - cnk_end # nearestKeyword => firstKeyword so cnk is in region before first keyword
        elif cnk_start > keyword_indices[keyword_size-1]:
            result = cnk_start - keyword_indices[keyword_size-1] # since cnk is in region after last keyword
        else:   # cnk is located between the first & last keywords i.e. ...firstKeyword...cnk...lastKeyWord...
            # format of region near cnk will look like: nearestLeftKeyWord...cnkStart
            # find index of nearestRightKeyword, then deduce index of nearestLeftKeyWord within keyword_indices, determine their respective indices and minimum distance of cnk to its nearest keyword
            nearest_right_keyword_index = get_nearest_right_keyword_for_enclosed_cnk(cnk_end)
            nearest_left_keyword_index = nearest_right_keyword_index - 1
            min_keyword_dist_to_right = keyword_indices[nearest_right_keyword_index] - cnk_end
            min_keyword_dist_to_left = cnk_start - keyword_indices[nearest_left_keyword_index]
            result = min(min_keyword_dist_to_right, min_keyword_dist_to_left)
    return result

def lemmatise_keyword_set(keywords_set):
    return {CONSTANTS.nlp(word)[0].lemma_.lower() for word in keywords_set} # lemmatised the keywords i.e. the root of the tree of each keyword

def summarise_snippet_by_getting_noun_chunks(snippet, keywords_set):
    """
    think of chunks as nouns or noun phrases
    """
    keywords_set = lemmatise_keyword_set(keywords_set)
    result = []
    doc = CONSTANTS.nlp(snippet)
    for chunk in doc.noun_chunks:
        if chunk.root.lemma_.lower() not in keywords_set:
            result.append(chunk.text) # the core noun in the noun chunk belongs to a non-keyword tree i.e. it is not a keyword, lemma of a keyword or inflection of a keyword
    return result

def summarise_snippet(snippet, keywords_set, is_noteworthy_word = is_noun_or_noun_phrase):
    """
    `is_noteworthy_word` is a function which examines a word and determines whether it is noteworthy or not, noteworthy words will be present in the summary that will be returned
    Think of it as a filtering tool
    """
    assert( isinstance(keywords_set,set))
    assert(len(snippet)>=1)
    snippet = snippet.split() # covnerts to list to allowing iterating through one word at a time (as opposed to chars)
    keywords_set = lemmatise_keyword_set(keywords_set) # convert keywords to their lemmatised form

    @functools.lru_cache(maxsize=128)
    def is_keyword(word):
        return get_lemma(word.lower()) in keywords_set
    
    def get_keyword_index_list(keywords_set, snippet):
        # identify all keywords (including inflections) in `snippet` & store their indexes in an array
        keyword_indices = [] # keyword_indices[i]: index of the ith keyword in `snippet`
        for i, word in enumerate(snippet):
            if is_keyword(word): # if lemma of word is in `keywords_set`, it means the word belongs to a keyword tree i.e. this word is part of a keyword tree, and is thus a keyword
                keyword_indices.append(i)
        return keyword_indices

    keyword_indices = get_keyword_index_list(keywords_set, snippet) # identify all keywords in `snippet` & store their indexes an array
    
    if len(keyword_indices) < 1: # snippet has none of the keywords, nor their inflections
        return []

    snippet_size = len(snippet)
    if snippet_size == 0: return "" # no keyword in snippet so ignore
    
    # at least 1 keyword exists so extract all noteworthy consecutive non-keywords (cnk), noteworthy cnks are non-keywords that pass the filter a.k.a filtrates
    # note there are 3 types of words: 1)keywords, 2a)non-keyword residue words (don't pass filter), 2b) non-keyword filtrate words
    # below algo iterates through `snippet` and plucks out all filtrate words, but if filtrate words are consecutive the sequence of consecutive filtrate words are plucked instead
    result_dict = dict() # stores key-value pairs, each noteworthy word/phrase mapped to the distance to its nearest keyword
    
    current = 0; # start inspection of `snippet` from first word
    while current < snippet_size: # not out of bounds (OOB)
        if is_keyword(snippet[current]) or is_noteworthy_word(snippet[current]) == False:
            current += 1
        else: 
            # current value is nonKeyword filtrate word, so find longest sequence of filtrates that starts with current word by
            # determining end of longest sequence of filtrate words i.e. find the next nonKeyword filtrate word
            cnk_start = current

            while (current < snippet_size) and ((not is_keyword(snippet[current])) and is_noteworthy_word(snippet[current]) == True):
                current += 1
            
            # regardless of the condition that caused termination of above loop, `current`-1 is the end of the cnk, so next iteration will start processing from `current`
            cnk_end = current-1
            distance_to_nearest_keyword = get_nearest_keyword_distance(cnk_start, cnk_end, keyword_indices)
            cnk = ' '.join(snippet[cnk_start:cnk_end+1])

            # store cnk in result_dict
            if cnk in result_dict:
                result_dict[cnk] = min(result_dict[cnk], distance_to_nearest_keyword) # if cnk has been extracted before, update distance to keyword with smallest 
            else:
                result_dict[cnk] = distance_to_nearest_keyword
            # next iteration will start processing from `current`, which currently holds the index of the word after the cnk
    
    result_list = [k for k,v in sorted(result_dict.items(), key=lambda item: item[1])] # sort result dictionary by value i.e. by item[1] then return keys ordered by their value
    return result_list