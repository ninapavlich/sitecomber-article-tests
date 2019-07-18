import logging
import re

from newspaper import Article
from newspaper.utils import get_available_languages

import readtime

from spellchecker import SpellChecker

logger = logging.getLogger('django')
spell = SpellChecker()


def get_article(page, settings):
    url = page.url
    html = page.latest_request.response.text_content

    language = 'en' if 'lang' not in settings else settings['lang']
    if language not in get_available_languages():
        logger.error(u"Language %s not found. Defaulting to 'en' instead." % (language))
        language = 'en'

    article = Article(url=url, language=language)
    article.download(html)
    article.parse()
    return article


def is_reader_view_enabled(page, settings):

    article = get_article(page, settings)

    reader_view_enabled = False
    messages = []
    if article.text and article.title:
        status = "success"
        reader_view_enabled = True
        messages.append(u"Page contains properly structured article.")

        if not article.top_image:
            messages.append(u"WARNING: Aricle missing top image.")
            status = "warning"
        if not article.top_image:
            messages.append(u"WARNING: Aricle missing authors.")
            status = "warning"
    else:
        messages.append(u"Page missing a structured article.")
        status = "error"

    message = u" ".join(messages)
    return reader_view_enabled, status, message


def contains_placeholder_text(page, settings):
    article = get_article(page, settings)

    placeholder_words = ['lorem', 'ipsum'] if 'placeholder_words' not in settings else settings['placeholder_words']

    if article.text:
        text_lower = article.text.lower() + article.title.lower()
        for placeholder_string in placeholder_words:
            if placeholder_string in text_lower:
                return True, u"Found placeholder word %s" % (placeholder_string)

    message = 'No placeholder text "%s" found.' % ('", "'.join(placeholder_words))
    return False, message


def get_article_readtime(page, settings):

    article = get_article(page, settings)
    if article.text:
        result = readtime.of_text(article.text)
        return str(result.text)

    return 'No article found'


def check_spelling(page, settings):

    article = get_article(page, settings)
    custom_known_words = [] if 'known_words' not in settings else settings['known_words']
    if article.text:

        check_words_raw = article.text.replace("\n", " ").replace("\r", " ").split(' ') + article.title.split(' ')
        punctuation_removed = [word.strip('?:!.,;') for word in check_words_raw if word]
        numbers_removed = [word for word in punctuation_removed if not re.search('\d+', word)]
        check_words = numbers_removed

        misspelled = [item for item in list(spell.unknown(check_words)) if item not in custom_known_words]
        print(check_words)
        print(misspelled)
        found_misspellings = len(misspelled) > 0
        message = "No misspellings found" if not found_misspellings else u'Found %s misspelling(s): "%s"' % (len(misspelled), '", "'.join(misspelled))
        return found_misspellings, message

    return True, 'No article found'
