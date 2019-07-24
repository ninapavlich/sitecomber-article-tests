import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sitecomber_article_tests'))
sys.path.append(BASE_DIR)

from sitecomber_article_tests.utils import get_misspelled_words, simplify_word
from sitecomber_article_tests.dictionary import core_dictionary


lang = "en"


def test_word(word):
    print(u"Testing word: %s" % (word))
    print(u"Is the word '%s' in the core dictionary? %s" % (word, (word in core_dictionary)))

    if (word not in core_dictionary):
        simplify_word(word, core_dictionary, True)

    get_misspelled_words(word, lang, core_dictionary)

test_word(input("Please enter a word to test: "))
