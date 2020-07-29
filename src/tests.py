from assimilation.queryResultAnalyser import summarise_snippet, summarise_snippet_by_getting_noun_chunks
import unittest

class TestStringMethods(unittest.TestCase):

    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_1(self):
        """
        checks that when the snippet of a search engine result is processed, only valid non-keywords are present in the summary result returned to the user.
        """
        snippet = """
        Nov 28, 2019 ... Stop dog barking noise is the best ultrasonic dog whistle sound app which will 
        produce anti dog bark sounds to stop barking dog sound
        """
    
        expectation = ['noise', 'ultrasonic', 'whistle sound app', 'bark sounds', 'sound', 'Nov']
        
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )
    
    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_2(self):
        snippet = """
        Collarless bark control solution humanely stops dog barking up to 200′ (60.1 m) 
        away – up to 4× farther than the competition. Powerful, humane, and ...
        """
        expectation = ['Collarless bark control solution', 'competition.', 'humane,']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )


    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_3(self):
        snippet = """
        Stops dog barking up to 300′ away – up to 6× farther than the competition while 
        still humane and shock-free. Worried about your dog this 4th of July? Check out ... 
        """
        expectation = ['300′', 'shock-free.', 'July?', 'competition']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )

    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_4(self):
        snippet = """
        Collarless bark control solution humanely stops dog barking up to 60 m away – 
        up ... Perfect for when you want to keep the peace with both your neighbour and ... 
        """
        expectation = ['Collarless bark control solution', 'Perfect', 'peace', 'neighbour']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )

    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_5(self):
        snippet = """
        Customers feel so relieved after purchasing as it stops dog barking effectively. ... 
        Obviously he has tried it on....but as soon as the noise kicks in(which is after the ... 
        """
        expectation = ['Customers', 'noise kicks in(which']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )


    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_6(self):
        snippet = """
        Stops Dog Barking with Humane, Painless Sound - Not Shock. (6 reviews). See 
        Reviews | Write a Review 4.56. HP-2 SUPER HUSH PUPPY: PROGRESSIVE ... 
        """
        expectation = ['Humane,', 'Sound', 'Shock.', 'reviews).', 'Reviews |', 'Review', 'HP-2 SUPER HUSH PUPPY: PROGRESSIVE']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )


    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_7(self):
        snippet = """
        All listings for this product. Buy It Now. Buy It Now. New. New. Dog Silencer® - 
        Ultrasonic Bark Control Device Stops Dog Barking Humanely. SPONSORED ... 
        """
        expectation = ['Silencer®', 'Ultrasonic Bark Control Device', 'SPONSORED', 'product.', 'listings']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )
    
    def test_that_null_list_is_returned_when_no_keywords_present_in_snippet_8(self):
        snippet = """
        This artificial intelligence based engine uses sound recognition to tell when
        """
        expectation = []
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )

    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_9(self):
        snippet = """
        This artificial intelligence based engine uses sound recognition to tell when a dog is barking
        """
        expectation = ['engine uses sound recognition', 'intelligence']
        keywords_set = {"stop","dog","barking"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )

    def test_only_valid_non_keywords_are_extracted_from_query_result_snippet_10(self):
        snippet = """
        give gone store dog
        """
        expectation = ['store']
        keywords_set = {"dog"}
        self.assertTrue( summarise_snippet(snippet, keywords_set) == expectation )

if __name__ == '__main__':
    unittest.main()