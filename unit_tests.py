import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'sitecomber_article_tests'))
sys.path.append(BASE_DIR)

from sitecomber_article_tests.unit_tests.spelling import test as spelling_test
from sitecomber_article_tests.unit_tests.placeholder import test as placeholder_test

placeholder_test()
spelling_test()
