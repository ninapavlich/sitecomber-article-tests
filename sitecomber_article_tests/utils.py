import logging
import re
from string import punctuation

from newspaper import Article
from newspaper.utils import get_available_languages

import nltk.data
from nltk.corpus import stopwords, words
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import SnowballStemmer

import contractions

import readtime

from spellchecker import SpellChecker

logger = logging.getLogger('django')


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

    # Validate that this is for English; currently only English is supported
    language = 'en' if 'lang' not in settings else settings['lang']
    # if language != 'en':
    #     return True, 'Language "%s" not supported' % (language)
    spell = SpellChecker(language=language, distance=1)

    # TODO -- translate two digit language code to full word:
    stop_words = set(stopwords.words('english'))
    dictionary = set(words.words())
    lmtzr = WordNetLemmatizer()
    snowball_stemmer = SnowballStemmer("english")

    article = get_article(page, settings)
    custom_known_words = [] if 'known_words' not in settings else settings['known_words']
    if article.text:

        raw_text = u'%s. %s' % (article.title, article.text)
        logger.debug("raw_text:")
        logger.debug(raw_text)

        # Replace fancy typigraphic characters like curly quotes and em dashes
        typographic_translation_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”–-—", u"'''\"\"---")])
        typography_removed = raw_text.translate(typographic_translation_table)
        hyphens_removed = typography_removed.replace("-", " ")
        newlines_removed = hyphens_removed.replace("\n", " ").replace("\r", " ")

        contractions_removed = contractions.fix(newlines_removed)
        possessives_removed = re.sub("\'s ", " ", contractions_removed)
        hyphens_removed = possessives_removed.replace("-", " ")
        acronyms_removed = re.sub(r"\b[A-Z\.]{2,}s?\b", "", hyphens_removed)

        whitespace_condensed = re.sub("[ \t]+", " ", acronyms_removed.replace(u'\u200b', ' '))

        # logger.info("whitespace_condensed:")
        # logger.info(whitespace_condensed)

        tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

        # Gather list of assumed proper nouns.
        # Assume anything capitalized in article is a local proper noun
        proper_nouns = []
        for sentence in tokenizer.tokenize(whitespace_condensed):
            sentence_words = [word for word in sentence.split(' ') if word]
            for word in sentence_words[1:]:
                if word and word[0].isupper() and (word.lower() not in stop_words):
                    proper_nouns.append(word.strip(punctuation))
        proper_nouns_lower = [word.lower() for word in proper_nouns]
        # logger.info("proper_nouns:")
        # logger.info(proper_nouns)

        # Split text into words
        check_words_raw = whitespace_condensed.split(' ')
        # logger.info("check_words_raw:")
        # logger.info(check_words_raw)

        # Remove stopwords for faster processing
        stopwords_removed = [word for word in check_words_raw if (word.lower() not in stop_words)]

        # Remove any numbers and punctuation
        punctuation_removed = [word.strip(punctuation) for word in stopwords_removed if (word and not re.search('\d+', word))]
        # logger.info("punctuation_removed:")
        # logger.info(punctuation_removed)

        remove_empty_words = [word for word in punctuation_removed if word]

        remove_custom_words = [word for word in remove_empty_words if (word not in custom_known_words)]

        # Remove anything matching a proper noun from above
        remove_proper_nounds = [item for item in remove_custom_words if item.lower() not in proper_nouns_lower]

        # Reduce to unique set of words
        check_words = list(set(remove_proper_nounds))
        # logger.info("check_words:")
        # logger.info(check_words)

        # First check the corpus dictionary:
        words_not_in_dict = [word for word in check_words if (word.lower() not in dictionary)]
        # logger.info("words_not_in_dict:")
        # logger.info(words_not_in_dict)

        unknown = [item for item in list(spell.unknown(words_not_in_dict))]
        # logger.info("unknown:")
        # logger.info(unknown)

        # Finally, try lemmatizing and stemming to see if root words are valid
        # TODO -- words like 'cartoonish' are getting flagged
        misspelled = []
        for word in unknown:
            lemmatized = lmtzr.lemmatize(word)
            if lemmatized not in dictionary:
                stemmed = snowball_stemmer.stem(word)
                if stemmed not in dictionary:
                    misspelled.append(word)

        logger.debug("misspelled:")
        logger.debug(misspelled)

        found_misspellings = len(misspelled) > 0
        message = "No misspellings found" if not found_misspellings else u'Found %s misspelling(s): "%s"' % (len(misspelled), '", "'.join(misspelled))
        return found_misspellings, message

    return False, 'No article found'
