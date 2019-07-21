from ..utils import get_misspelled_words, simplify_word


"""
Outstanding mis idenified words:
- moms
- paycheck
- hashtag
- sleepover
"""


def test():
    words_to_simplify = ['mustardy', 'misstated', 'rashy', 'rashiness', 'toddlerhood',
                         'clinginess', 'seatmates', 'grandparenting', 'moisterizers']
    expected_output = ['mustard', 'misstate', 'rash', 'rash', 'toddler', 'cling', 'seat', 'grandparent', 'moist']
    output = []
    for word in words_to_simplify:
        output.append(simplify_word(word))

    if output != expected_output:
        raise Exception("Words incorrectly simplified from:\n%s to:\n%s expected:\n%s" % (words_to_simplify, output, expected_output))

    test_text = """
This is an example with proper nouns Dr. Marelle Jazdin, a doctor. Marelle Jazdin is a doctor. Jazdin thinks you should be mindful.
Acronym test: ABCD, A.B.C.D, and even A.B.C.Ds.
Fancy typography test: This is a sentence with fancy curly quotes,” it’s great to have fancy typography like ‘single quotes’ ´back ticks various dashes –-—⁃ ellipses … and fancy bullets •∙
Email test: abc user@xxx.com 123 any@www foo @ bar 78@ppp @5555 aa@111 testing @MyFancyHandle and use the hash tag #fancyhashtag
Words separated by slashes: and/or happy/sad/etc
Compound words test: grandparenting, toddlerhood, seatmates, mustardy, hallucinated, moisterizers, misstated, rashy, clinginess
    """

    misspelled_words = get_misspelled_words(test_text, "en")
    if len(misspelled_words) > 0:
        raise Exception("Words incorrectly flagged: %s" % (misspelled_words))
