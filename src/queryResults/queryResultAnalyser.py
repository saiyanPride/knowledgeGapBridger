import functools
import spacy
nlp = spacy.load('en_core_web_sm')
PENN_TREEBANK_POS_TAGS_NOUNS = ["NN","NNP","NNS","NNPS"]
END_OF_SUMMARY_DELIMETER = ";"

def info(msg): print("[INFO] " + msg)

def get_nearest_keyword_distance(cnk_start, cnk_end, keyword_ranks):
    """
    keyword_ranks has to be non-empty list!
    keyword_ranks[i] is the rank of keyword i within the query result snippet. 

    cnk refers to a consecutive non-keyword: it could be a single word or a collection of words(phrase) which have been deemed noteworthy, 
    thus it will be included in the summary of the snippet being processed
    
    Rank of a word refers to its order in the snippet string, so the ith word in the snippet has a rank of i where i=1,2,3,...
    There is an implicit assumption, that the snippet will only be a few words i.e. not billions of words, otherwise integer overflows may occur when dealing with ranks e.g. the 5 billionth word's rank can't be stored in a 32 bit int
    """
    keyword_size = len(keyword_ranks)
    assert(keyword_size >= 1)
    assert(cnk_start <= cnk_end)
    result = 0

    def get_nearest_right_keyword_for_enclosed_cnk(cnk_rank): #nested
        """
        cnk is guaranteed to be surrounded by keywords i.e. it has a nearest left keyword
        """
        nearest_right_keyword_index = -1
        for i in range(0,keyword_size): # find index in keyword_ranks corresponding to nearestRightKeyword 
            if keyword_ranks[i] > cnk_rank: 
                nearest_right_keyword_index = i
        assert(nearest_right_keyword_index != -1)# this assertion is redundant, it is guaranteed that the nearest_right_keyword_index was found and set
        return nearest_right_keyword_index
        

    if cnk_start == cnk_end: # cnk is a single word
        cnk_rank = cnk_start
        
        if keyword_size == 1: # handle case for 1 keyword
            result = abs(keyword_ranks[0]- cnk_rank)
        elif cnk_rank < keyword_ranks[0]: # cnk is to the left of first keyword i.e. cnk...firstKeyword
            result = keyword_ranks[0]- cnk_rank
        elif cnk_rank > keyword_ranks[keyword_size-1]: # cnk is to the right of last keyword i.e. lastKeyword...cnk
            result = cnk_rank - keyword_ranks[keyword_size-1]
        else: # cnk enclosed by 2 keywords on either side i.e. nearestLeftKeyWord...cnk...nearestRightKeyword
            # find rank of nearestRightKeyword, and use it to determine rank of nearestLeftKeyWord
            nearest_right_keyword_index = get_nearest_right_keyword_for_enclosed_cnk(cnk_rank)
            nearest_left_keyword_index = nearest_right_keyword_index - 1
            result = min(keyword_ranks[nearest_right_keyword_index] - cnk_rank, cnk_rank - keyword_ranks[nearest_left_keyword_index])
    else: # cnk consists of >=2 consective words i.e. cnk_start < cnk_end
        if keyword_size == 1: # the sole keyword is either to the left or right of the cnk
            result = cnk_start - keyword_ranks[0] if keyword_ranks[0] < cnk_start else keyword_ranks[0] - cnk_end
        elif cnk_end < keyword_ranks[0]: # keyword_size is guaranteed to be >=2 since if this line reached i.e. we have this snippet general form 
                                            # ...firstKeyword...lastKeyWord...), so handle cases where is cnk located in each of the 3 regions (...)
            result = keyword_ranks[0] - cnk_end # nearestKeyword => firstKeyword so cnk is in region before first keyword
        elif cnk_start > keyword_ranks[keyword_size-1]:
            result = cnk_start - keyword_ranks[keyword_size-1] # since cnk is in region after last keyword
        else:   # cnk is located between the first & last keywords i.e. ...firstKeyword...cnk...lastKeyWord...
            # format of region near cnk will look like: nearestLeftKeyWord...cnkStart
            # find index of nearestRightKeyword, then deduce index of nearestLeftKeyWord within keyword_ranks, determine their respective ranks and minimum distance of cnk to its nearest keyword
            nearest_right_keyword_index = get_nearest_right_keyword_for_enclosed_cnk(cnk_end)
            nearest_left_keyword_index = nearest_right_keyword_index - 1
            min_keyword_dist_to_right = keyword_ranks[nearest_right_keyword_index] - cnk_end
            min_keyword_dist_to_left = cnk_start - keyword_ranks[nearest_left_keyword_index]
            result = min(min_keyword_dist_to_right, min_keyword_dist_to_left)
    return result

def is_noun_or_noun_phrase(word):
    token = nlp(word)[0]
    result = True if token.tag_ in PENN_TREEBANK_POS_TAGS_NOUNS else False
    return result

def lemmatise_keyword_set(keywords_set):
    return {nlp(word)[0].lemma_ for word in keywords_set} # lemmatised the keywords i.e. the root of the tree of each keyword

def summarise_snippet_get_noun_chunks(snippet, keywords_set):
    """
    think of chunks as nouns or noun phrases
    """
    keywords_set = lemmatise_keyword_set(keywords_set)
    result = []
    doc = nlp(snippet)
    for chunk in doc.noun_chunks:
        if chunk.root.lemma_ not in keywords_set:
            result.append(chunk.text) # the core noun in the noun chunk belongs to a non-keyword tree i.e. it is not a keyword, lemma of a keyword or inflection of a keyword
    return result

def get_lemma(word):
    return nlp(word)[0].lemma_
def summarise_snippet(snippet, keywords_set, is_noteworthy_word = is_noun_or_noun_phrase):
    """
    is_noteworthy_word is a function which examines a word and determines whether it is noteworthy or not, noteworthy words will be present in the summary that will be returned
    Think of it as a filtering tool
    """
    assert( isinstance(keywords_set,set))
    assert(len(snippet)>=1)
    snippet = snippet.split() # covnerts to list to allowing iterating through one word at a time (as opposed to chars)

    # identify all keywords & store their indexes an array

    snippet_size = len(snippet)
    keyword_rank_list = [] # keyword_rank_list[i] rank of the ith keyword encountered
    keywords_set = lemmatise_keyword_set(keywords_set)
    
    @functools.lru_cache(maxsize=128)
    def is_keyword(word):
        return get_lemma(word.lower()) in keywords_set

    for i, word in enumerate(snippet):
        if is_keyword(word): # if lemma of word is in `keywords_set`, it means the word belongs to a keyword tree i.e. this word is part of a keyword tree, and is thus a keyword
            keyword_rank_list.append(i)

    
    if len(keyword_rank_list) < 1:
        return []
    """
    #DEBUG start
        print("this snippet has no inflection of any of the keywords")
        print("keywords are: ", keywords_set)
        print("snippet is: ", snippet)
        print("keyword rank list: ", keyword_rank_list)
        assert(len(keyword_rank_list) >= 1)
    #DEBUG end
    """
    result_dict = dict() # stores key-value pairs, each noteworthy word/phrase mapped to its distance to its nearest keyword
    if snippet_size == 0: return "" # no keyword in snippet so do nothing
    else: # at least 1 keyword exists so extract all noteworthy consecutive non-keywords (cnk), noteworthy cnks are non-keywords that pass the filter a.k.a filtrates
        # note there are 3 types of words: 1)keywords, 2a)non-keyword residue words (don't pass filter), 2b) non-keyword filtrate words
        # below algo plucks out all filtrate words, but if filtrate words are consecutive, pluck them all out
        current = 0; # start from first word
        while current < snippet_size: # not out of bounds (OOB)
            if is_keyword(snippet[current]) or is_noteworthy_word(snippet[current]) == False:
                current += 1
            else: # current value is nonKeyWord filtrate word, so find longest sequence of filtrates that starts with current word, to form cnk
                # determine end of longest sequence of filtrate words i.e. find the next nonKeyWord filtrate word
                cnk_start = current

                while (current < snippet_size) and ((not is_keyword(snippet[current])) and is_noteworthy_word(snippet[current]) == True):
                    current += 1
                
                # regardless of the condition that caused termination, `current`-1 is the end of the cnk, so next iteration will start processing from `current`
                cnk_end = current-1
                min_distance_to_keyword = get_nearest_keyword_distance(cnk_start, cnk_end, keyword_rank_list)
                cnk = ' '.join(snippet[cnk_start:cnk_end+1])

                # store cnk in result_dict
                if cnk in result_dict:
                    result_dict[cnk] = min(result_dict[cnk], min_distance_to_keyword) # if cnk has been extracted before, update distance to keyword with smallest 
                else:
                    result_dict[cnk] = min_distance_to_keyword
                # next iteration will start processing from `current`, which currently holds the index of the word after cnk
    
    result_list = [k for k,v in sorted(result_dict.items(), key=lambda item: item[1])] # sort result dictionary by value i.e. by item[1] then returns keys ordered by their value
    return result_list
if __name__ == '__main__':
    snippet1 = """
    Nov 28, 2019 ... Stop dog barking noise is the best ultrasonic dog whistle sound app which will 
    produce anti dog bark sounds to stop barking dog sound
    """

    snippet2 = """
    Collarless bark control solution humanely stops dog barking up to 200′ (60.1 m) 
    away – up to 4× farther than the competition. Powerful, humane, and ...
    """
    snippet3 = """
    Stops dog barking up to 300′ away – up to 6× farther than the competition while 
    still humane and shock-free. Worried about your dog this 4th of July? Check out ... 
    """

    snippet4 = """
    Collarless bark control solution humanely stops dog barking up to 60 m away – 
    up ... Perfect for when you want to keep the peace with both your neighbour and ... 
    """

    snippet5 = """
    Customers feel so relieved after purchasing as it stops dog barking effectively. ... 
    Obviously he has tried it on....but as soon as the noise kicks in(which is after the ... 
    """

    snippet6 = """
    Stops Dog Barking with Humane, Painless Sound - Not Shock. (6 reviews). See 
    Reviews | Write a Review 4.56. HP-2 SUPER HUSH PUPPY: PROGRESSIVE ... 
    """

    snippet7 = """
    All listings for this product. Buy It Now. Buy It Now. New. New. Dog Silencer® - 
    Ultrasonic Bark Control Device Stops Dog Barking Humanely. SPONSORED ... 
    """

    keywords_set = {"stop","dog","barking"}

    snippets = [snippet1, snippet2, snippet3, snippet4, snippet5, snippet6, snippet7]
    
    print("--RESULTS---")

    for snippet in snippets:
        print("nuggets ordered by minDist ->", summarise_snippet(snippet, keywords_set))
        print("noun chunks ->", summarise_snippet_get_noun_chunks(snippet, keywords_set))
        print("\n")