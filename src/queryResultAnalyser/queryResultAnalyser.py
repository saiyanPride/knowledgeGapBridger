def get_nearest_keyword_distance(cnk_start, cnk_end, keyword_ranks):
  """
  `keywordRanks` has to be non-empty list!; keywordRanks[i] is the rank of keyword i within the snippet. 
  Rank of a word refers to its order in the snippet string, hint: 1st word in the snippet has a rank of 1, 2nd word has a rank of 2 and so on
  There is an implicit assumption, that the snippet would only be a few words i.e. not billions of words, otherwise integer overflows may occur when dealing with ranks e.g. the 5 billionth word's rank can't be stored in 32 bit int
  """
  assert(len(keyword_ranks) >= 1)
  assert(cnk_start <= cnk_end)
  # if(start == end), cnk is a single word
    # cnk_rank = start
    # handle case for 1 keyword => minDist = abs(keyword_ranks[0]- cnk_rank); 
    # handle case for at least 2 keywords
    # if rank(cnk) < rank(firstKeyword) nearestKeyword => firstKeyword
    # elif rank(wordi) > rank(lastKeyword) nearestKeyword => lastKeyword
    # else: nonkeywordi is enclosed by 2 keywords, determine the nearest one to left & right, then find minimum distance
      #minDistRight: iterate from leftmostkeyword and find first rank larger than `cnkRank`, we know one exists, then find distance
      #minDistLeft: lbKeyword is the one just before the upper bound keyword
      #minDistance = min(minDistLeft,minDistRight)
      #.nearestLeftKeyWord...cnk...nearestRightKeyword
  # if(start < end), cnk has at least 2 words
    # handle case for 1 keyword
      #keyword is either to the left or the right of cnk
      # if keywordRank < cnkStart, minDist = cnkStart-keywordRank
      # else minDist = keywordRank - cnkEnd
    # handle case for >=2 keywordRanks
      # ...firstKeyword...lastKeyWord...; where is cnk located out of the 3 regions
      # if (cnkEnd < rank(firstKeyword)) ; cnk is in region before first keyword
        #nearestKeyword => firstKeyword, minDist = rank(firstKeyword) -cnkEnd
      # if (cnkStart > rank(lastKeyword), minDist = cnkStart - rank(lastKeyword)
      # else we know we have this case: ...firstKeyword...cnk...lastKeyWord...
      # this means from cnk's perspective we have
      # nearestLeftKeyWord...cnkStart->cnkEnd...nearestRightKeyword, the gaps in this case contain 0 or more words e.g. 
        #iterate through the keyword ranks, and find first rank larger than cnkEnd => minDistRight = rank(nearestRightKeyword) -cnkEnd
       # minDistLeft = cnkStart - rank(nearestLeftKeyWord), where rank(nearestLeftKeyWord) is the rank of keyword to the immediate left of nearestRightKeyword
        # minDist = min(minDistLeft,minDistRight) 
  pass
def summarise_snippet(snippet, keywords_set, is_noteworthy_word):
    assert(len(snippet)>=1)
    # store the index of all keywords in an array
    
    snippet_size = len(snippet)
    keyword_rank_list = [ snippet[i] if snippet[i] in keywords_set for i in range(0,snippet_size)] # keyword_rank_list[i] rank of the ith keyword encountered

    result_dict = dict() # stores key-value pairs, each noteworthy word/phrase mapped to its distance to its nearest keyword
    if snippet_size == 0: return "" # no keyword in snippet so do nothing
    else: # at least 1 keyword exists so extract all noteworthy consecutive non-keywords (cnk), noteworthy cnks are non-keywords that pass the filter a.k.a filtrates
        # note there are 3 types of words: 1)keywords, 2a)non-keyword residue words (don't pass filter), 2b) non-keyword filtrate words
        # below algo plucks out all filtrate words, but if filtrate words are consecutive, pluck them all out
        current = 0; # start from first word
        while current < snippet_size: # not out of bounds (OOB)
            if snippet[current] in keywords_set or is_noteworthy_word(snippet[current]) == False:
                current += 1
            else: # current value is nonKeyWord filtrate word, so find longest sequence of filtrates that starts with current word, to form cnk
                # determine end of longest sequence of filtrate words i.e. find the next nonKeyWord filtrate word
                cnk_start = current
                while (current < snippet_size) and (snippet[current] in keywords_set or (is_noteworthy_word(snippet[current]) == False) ):
                    current += 1
                
                # regardless of the condition that caused termination, `current`-1 is the end of the cnk, so next iteration will start processing from `current`
                cnk_end = current
                min_distance_to_keyword = get_nearest_keyword_distance(cnk_start, cnk_end, keyword_rank_list)
                cnk = snippet[cnk_start:cnk_end+1]

                # store cnk in result_dict
                if result_dict.has_key(cnk):
                    result_dict[cnk] = min(result_dict[cnk], min_distance_to_keyword) # if cnk has been extracted before, update distance to keyword with smallest 
                else:
                    result_dict[cnk] = min_distance_to_keyword
                # next iteration will start processing from `current`, which currently holds the index of the word after cnk
    
    result_list = [k for k,v in sorted(result_dict.items(), key=lambda item: item[1])] # sort result dictionary by value i.e. by item[1] then returns keys ordered by their value
    return '\t;\t'.join(result_list)