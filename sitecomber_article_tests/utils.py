import logging
import re
from string import punctuation

from newspaper import Article
from newspaper.utils import get_available_languages

import nltk.data
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.stem import SnowballStemmer

import contractions

import readtime

from spellchecker import SpellChecker

from .dictionary import dictionary


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
    data = {}
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

        data = {
            'article': {
                'text': article.text,
                'title': article.title,
                'authors': article.authors,
                'publish_date': article.publish_date,
                'top_image': article.top_image,
                'imgs': list(article.imgs)
            }
        }
    else:
        messages.append(u"Page missing a structured article.")
        status = "error"

    message = u" ".join(messages)
    return reader_view_enabled, status, message, data


def contains_placeholder_text(page, settings):
    article = get_article(page, settings)

    placeholder_words = ['lorem', 'ipsum'] if 'placeholder_words' not in settings else settings['placeholder_words']
    data = {'placeholder_words_searched': placeholder_words, 'placeholder_words_found': []}
    placeholder_words_found = []
    if article.text:
        text_lower = article.text.lower() + article.title.lower()
        for placeholder_string in placeholder_words:
            if placeholder_string in text_lower:
                placeholder_words_found.append(placeholder_string)

    data['placeholder_words_found'] = placeholder_words_found
    if len(placeholder_words_found) > 0:
        return True, u"Found placeholder word(s) %s" % ('", "'.join(placeholder_words_found)), data
    else:
        message = 'No placeholder text "%s" found.' % ('", "'.join(placeholder_words))
        return False, message, data


def get_article_readtime(page, settings):

    article = get_article(page, settings)
    if article.text:
        result = readtime.of_text(article.text)
        return str(result.text), {'read_time': str(result.text)}

    return 'No article found', {}


def check_spelling(page, settings):
    # Validate that this is for English; currently only English is supported
    language = 'en' if 'lang' not in settings else settings['lang']

    article = get_article(page, settings)
    custom_known_words = [] if 'known_words' not in settings else settings['known_words']
    if article.text:
        raw_text = u'%s. %s' % (article.title, article.text)
        misspelled = get_misspelled_words(raw_text, language, custom_known_words)
        found_misspellings = len(misspelled) > 0
        message = "No misspellings found" if not found_misspellings else u'Found %s misspelling(s): "%s"' % (len(misspelled), '", "'.join(misspelled))
        return found_misspellings, message, {'misspelled_words': misspelled}

    return False, 'No article found', {}

suffixes = ['able', 'acy', 'al', 'al', 'ance', 'ate', 'bility', 'bio', 'dom', 'ed', 'en', 'ence', 'er', 'erizer', 'es', 'esque', 'est', 'ful', 'fy', 'hood', 'ible', 'ic', 'ical', 'ied', 'ier', 'ies', 'iest', 'ify', 'iness', 'ing', 'ious', 'ise', 'ish', 'ism', 'ist', 'ity', 'ive', 'ize', 'izer', 'less', 'like', 'long', 'ly', 'mate', 'ment', 'ness', 'ologist', 'ous', 'pping', 'red', 'sion', 'ting', 'tion', 'tize', 'tted', 'ty', 'ward', 'wards', 'wide', 'wise', 'worthy', 'y', 'zing']
suffix_replacements = {
    'bility': ['ble'],
    'iness': ['y'],
    'ied': ['y'],
    'ier': ['y'],
    'ies': ['y'],
    'iest': ['y'],
    'ity': ['y'],
    'ed': ['e'],
    'es': ['e'],
    'er': ['e'],
    'ence': ['e'],
    'ing': ['e'],
    'ologist': ['ology'],
    'pping': ['p'],
    'red': ['re'],
    'tize': ['ty', 't'],
    'tted': ['t'],
    'tion': ['te'],
    'ting': ['te', 't'],
    'zing': ['ze', 'z']
}

prefixes = ['ante', 'anti', 'auto', 'bi', 'bis', 'co', 'de', 'dis', 'en', 'ex', 'extra', 'hyper', 'ig', 'im', 'in', 'inter', 'ir', 'macro', 'mal', 'mega', 'micro', 'mini', 'mis', 'mono', 'multi', 'neo', 'neuro', 'non', 'omni', 'over', 'penta', 'per', 'poly', 'post', 'pre', 'pro', 'quad', 're', 'retro', 'semi', 'socio', 'sub', 'super', 'tran', 'tri', 'un', 'under', 'uni']
# Sort prefixes and suffixes from longest to shortest
suffixes.sort(key=lambda s: len(s))
suffixes.reverse()
prefixes.sort(key=lambda s: len(s))
prefixes.reverse()


stop_words = set(stopwords.words('english'))
lmtzr = WordNetLemmatizer()
snowball_stemmer = SnowballStemmer("english")


def replace_prefix(word, debug=False):
    log_level = logging.WARNING if debug else logging.DEBUG
    for prefix in prefixes:
        if word.startswith(prefix):
            word_updated = word[len(prefix):]
            logger.log(log_level, u"Attempting to remove prefix '%s' from word %s.... %s" % (prefix, word, word_updated))
            if word_updated in dictionary:
                logger.log(log_level, u"Removing prefix '%s' from word %s: %s --> %s" % (prefix, word, word_updated, (word_updated in dictionary)))
                return word_updated

    return word


def replace_suffix(word, debug=False):
    log_level = logging.WARNING if debug else logging.DEBUG
    for suffix in suffixes:
        if word.endswith(suffix):
            word_updated = word[0:-len(suffix)]
            logger.log(log_level, u"Attempting to remove suffix '%s' from word %s....%s" % (suffix, word, word_updated))
            if word_updated in dictionary:
                logger.log(log_level, u"Removing suffix '%s' from word %s: %s --> %s" % (suffix, word, word_updated, (word_updated in dictionary)))
                return word_updated

            prefix_replaced = replace_prefix(word_updated, debug)
            if prefix_replaced in dictionary:
                logger.log(log_level, u"Removing suffix '%s' and prefix from word %s: %s --> %s" % (suffix, word, prefix_replaced, (prefix_replaced in dictionary)))
                return prefix_replaced

            # suffix may need to be replaced with better ending
            if suffix in suffix_replacements:
                for suffix_replacement in suffix_replacements[suffix]:
                    replaced = word.replace(suffix, suffix_replacement)
                    logger.log(log_level, u"Attempting to replace suffix '%s' with '%s' to get %s" % (suffix, suffix_replacement, replaced))
                    if replaced in dictionary:
                        logger.log(log_level, u"Removing suffix '%s' from word %s: %s --> %s" % (suffix, word, replaced, (replaced in dictionary)))
                        return replaced

                    prefix_replaced = replace_prefix(replaced, debug)
                    if prefix_replaced in dictionary:
                        logger.log(log_level, u"Removing suffix '%s' and prefix from word %s: %s --> %s" % (suffix, word, prefix_replaced, (prefix_replaced in dictionary)))
                        return prefix_replaced

    return word


def simplify_word(word, debug=False):
    log_level = logging.WARNING if debug else logging.DEBUG

    original_word = word
    logger.log(log_level, u"\n--------- Simplifying %s ---------" % (word))

    # simple singularlize:
    if word.endswith('s') and word[0:-1] in dictionary:
        logger.log(log_level, "Simple singularization returns valid word %s" % (word[0:-1]))
        return word[0:-1]

    word = replace_suffix(word, debug)
    if word in dictionary:
        logger.log(log_level, "First round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word, debug)
    if word in dictionary:
        logger.log(log_level, "First round prefix replaced to get valid word %s" % (word))
        return word

    # simple singularlize:
    if word.endswith('s'):
        word = word[0:-1]
        if word in dictionary:
            logger.log(log_level, "Second round singularization replaced to get valid word %s" % (word))
            return word

    word = replace_suffix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Second round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Second round prefix replaced to get valid word %s" % (word))
        return word

    # simple singularlize:
    if word.endswith('s'):
        word = word[0:-1]
        if word in dictionary:
            logger.log(log_level, "Third round singularization replaced to get valid word %s" % (word))
            return word

    word = replace_suffix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Third round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Third round prefix replaced to get valid word %s" % (word))
        return word

    # Now try lemmatizing / stemming
    lemmatized = lmtzr.lemmatize(original_word)
    if lemmatized in dictionary:
        logger.log(log_level, "Lemmatizer returned valid word %s" % (lemmatized))
        return lemmatized

    stemmed = snowball_stemmer.stem(original_word)
    if stemmed in dictionary:
        logger.log(log_level, "Stemmer returned valid word %s" % (stemmed))
        return stemmed

    # Now try starting with prefixes first:
    word = original_word
    if word.endswith('s') and word[0:-1] in dictionary:
        logger.log(log_level, "Simple singularization returns valid word %s" % (word[0:-1]))
        return word[0:-1]

    word = replace_prefix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Fourth round prefix replaced to get valid word %s" % (word))
        return word

    word = replace_suffix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Fourth round suffix replaced to get valid word %s" % (word))
        return word

    # simple singularlize:
    if word.endswith('s'):
        word = word[0:-1]
        if word in dictionary:
            logger.log(log_level, "Fifth round singularization replaced to get valid word %s" % (word))
            return word

    word = replace_suffix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Fifth round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word, debug)
    if word in dictionary:
        logger.log(log_level, "Fifth round prefix replaced to get valid word %s" % (word))
        return word

    logger.log(log_level, "No simplified version found, return original %s" % (original_word))
    return original_word


def get_misspelled_words(raw_text, language, custom_known_words=[]):

    # if language != 'en':
    #     return True, 'Language "%s" not supported' % (language)
    spell = SpellChecker(language=language, distance=1)

    logger.debug("raw_text:")
    logger.debug(raw_text)

    # Replace fancy typigraphic characters like curly quotes and em dashes
    typographic_translation_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´'“”–-—⁃‐…●•∙", u"''''\"\"-----.---")])
    typography_removed = raw_text.translate(typographic_translation_table)
    hyphens_removed = typography_removed.replace("-", " ").replace("/", " ")
    newlines_removed = hyphens_removed.replace("\n", " ").replace("\r", " ")

    # Remove email addresses, hashes, urls, phone numbers...
    emails_removed = re.sub(r"\S*@\S*\s?", "", newlines_removed)
    hashes_removed = re.sub(r"#(\w+)", "", emails_removed)
    phonenumbers_removed = re.sub(r"(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", "", hashes_removed)
    urls_removed = re.sub(r"([\w\.]+\.(?:com|org|net|us|co|edu|gov|uk)[^,\s]*)", "", phonenumbers_removed)

    contractions_removed = contractions.fix(urls_removed)
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
        for word in sentence_words:
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
        simplified_word = simplify_word(word)
        if simplified_word not in dictionary:
            misspelled.append(simplified_word)

    logger.debug("misspelled:")
    logger.debug(misspelled)

    return misspelled
