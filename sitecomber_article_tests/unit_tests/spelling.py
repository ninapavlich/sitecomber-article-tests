from ..utils import get_misspelled_words, simplify_word
from ..dictionary import core_dictionary

"""
Outstanding mis idenified words:
- moms
- paycheck
- hashtag
- sleepover
- bandanas
- restroom
- sanitizer
- handwash
- descrimination
"""


def test():

    words_to_simplify = ['mustardy', 'misstated', 'rashy', 'rashiness',
                         'toddlerhood', 'clinginess', 'seatmates',
                         'grandparenting', 'moisterizers', 'recertified',
                         'cringeworthy', 'reoccurred', 'misappropriating',
                         'handwashing', 'declutter', 'unshowered',
                         'underappreciated', 'reconfigured', 'cataloging']
    expected_output = ['mustard', 'misstate', 'rash', 'rash', 'toddler',
                       'cling', 'seat', 'grandparent', 'moist', 'recertify',
                       'cringe', 'reoccur', 'misappropriate', 'handwash',
                       'clutter', 'shower', 'appreciate',
                       'configure', 'catalog']
    output = []
    for word in words_to_simplify:
        output.append(simplify_word(word, core_dictionary, True))

    if output != expected_output:
        raise Exception("Words incorrectly simplified from:\n%s to:\n%s expected:\n%s" % (words_to_simplify, output, expected_output))

    test_text = u"""
This is an example with proper nouns Dr. Marelle Jazdin, a doctor. Marelle Jazdin is a doctor. Jazdin thinks you should be mindful.
Acronym test: ABCD, A.B.C.D, and even A.B.C.Ds.
Fancy typography test: This is a sentence with fancy curly quotes,” it’s great to have fancy typography like ‘single quotes’ ´back ticks various dashes –-—⁃ ellipses … and fancy bullets •∙
Email test: abc user@xxx.com 123 any@www foo @ bar 78@ppp @5555 aa@111 testing @MyFancyHandle and use the hash tag #fancyhashtag
URL Test: http://www.example1.com example2.com https://example3.com
Words separated by slashes: and/or happy/sad/etc
Compound words test: grandparenting, toddlerhood, seatmates, mustardy, hallucinated, moisterizers, misstated, rashy, clinginess,
sanitizers handwashing recertified bandanas restrooms desensitized weepier scrunchies misappropriating iphones gummy candy yearslong medicating flatline telecommute
emailed transvaginal commoditize counterintuitively pickiest well‐to‐do breast‐feeding nonbinding veganism baby's underappreciated trademarked
hypercompetitive reconfigured dumbest adjustability unshowered prepped women's declutter surefootedness cataloging e-commerce cannibalized keychains
"""
    print("Getting misspelled words - round 1...")
    misspelled_words = get_misspelled_words(test_text, "en", core_dictionary)
    if len(misspelled_words) > 0:
        raise Exception("Words incorrectly flagged. Should have found 0 misspellings, but instead found: %s" % (misspelled_words))

    print("Getting misspelled words - round 2...")
    test_text_with_errors = u"""asdl238() 29UDUDJS asdflkjd"""
    misspelled_words = get_misspelled_words(test_text_with_errors, "en", core_dictionary)
    if len(misspelled_words) == 0:
        raise Exception("Words incorrectly flagged. Should have found at least one misspelling from %s" % (test_text_with_errors))

    print("Done!")
