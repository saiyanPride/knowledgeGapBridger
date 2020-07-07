/*
This file will be compiled and configured to enable invocation of its commands from python
The computations here are expected to be computationally demanding
*/
#include <string>
#include <cstdint>
using namespace std;
/*
Think of `ResultCandidates` as words & phrases that are extracted from the pages/urls returned from a search engine query
*/
class ResultCandidates{
    string name;
    uint64_t noRelatedKeywords; //  no of keywords in the query, that this resultcandidate is related to
    vector<uint64_t> averageDistanceToKeyword; // averageDistanceToKeyword[i] is the avg distance of this resultcandidate to keyword i of the query
    vector<uint64_t> minDistanceToKeyword;
    vector<uint64_t> maxDistanceToKeyword;
    uint64_t minAverageDistanceToKeyword, maxAverageDistanceToKeyword;
    uint64_t minDistanceToKeyword, maxDistanceToKeyword; //a small min/max distance could be an indication that this resultcandidate was in the same sentence as the keyword, or in a nearby sentence
    uint64_t totalAssociationFrequency;
    
    public:
    
    ResultCandidates(string name_): name(name_){
        noRelatedKeywords = minAverageDistanceToKeyword = maxAverageDistanceToKeyword = associationFrequencyToKeywordsSum = 0;
    }

    uint64_t noRelatedKeywords();
    uint64_t minAverageDistanceToKeyword();
    uint64_t maxAverageDistanceToKeyword();
    uint64_t totalAssociationFrequency();
    uint64_t minDistanceToKeyword();
    uint64_t maxDistanceToKeyword();
};

/*
- no of keywords that it relates to
- average distance to each keyword and thus min & max average keyword distance
- min & max distance to keyword, to give a range
- overall frequency of association with all keywords i.e. sum of freq of association with each keyword
*/