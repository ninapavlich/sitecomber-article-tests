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

    article = get_article(page, settings)
    custom_known_words = [] if 'known_words' not in settings else settings['known_words']
    if article.text:
        raw_text = u'%s. %s' % (article.title, article.text)
        misspelled = get_misspelled_words(raw_text, language, custom_known_words)
        found_misspellings = len(misspelled) > 0
        message = "No misspellings found" if not found_misspellings else u'Found %s misspelling(s): "%s"' % (len(misspelled), '", "'.join(misspelled))
        return found_misspellings, message

    return False, 'No article found'

suffixes = ['able', 'acy', 'al', 'al', 'ance', 'ate', 'dom', 'ed', 'en',
            'ence', 'er', 'es', 'esque', 'ful', 'fy', 'hood', 'ible', 'ic',
            'ical', 'ify', 'iness', 'ing', 'ious', 'ise', 'ish', 'ism', 'ist',
            'ity', 'ive', 'ize', 'izer', 'less', 'ly', 'mate', 'ment', 'ness', 'ous',
            'sion', 'tion', 'ty', 'ward', 'wards', 'wise', 'y']
suffix_replacements = {
    'iness': 'y',
    'ed': 'e',
    'es': 'e',
    'er': 'e',
    'ence': 'e'
}
prefixes = [
    'ante', 'anti', 'auto', 'bi', 'bis', 'co', 'de', 'dis', 'ex', 'extra', 'in',
    'ig', 'ir', 'im', 'en', 'inter', 'macro', 'micro', 'mega', 'mini', 'mal',
    'mono', 'multi', 'mis', 'non', 'omni', 'penta', 'per', 'poly', 'post', 'pre',
    'pro', 'quad', 're', 'retro', 'semi', 'sub', 'super', 'tran', 'tri', 'un', 'uni']
# Sort prefixes and suffixes from longest to shortest
suffixes.sort(key=lambda s: len(s))
suffixes.reverse()
prefixes.sort(key=lambda s: len(s))
prefixes.reverse()


stop_words = set(stopwords.words('english'))
dictionary = set(words.words())
lmtzr = WordNetLemmatizer()
snowball_stemmer = SnowballStemmer("english")


def replace_prefix(word):
    for prefix in prefixes:
        if word.startswith(prefix):
            word_updated = word[len(prefix):]
            logger.warn("Removing prefix %s from word %s: %s" % (prefix, word, word_updated))
            word = word_updated

            break
    return word


def replace_suffix(word):
    for suffix in suffixes:
        if word.endswith(suffix):
            word_updated = word[0:-len(suffix)]
            if word_updated not in dictionary:
                if suffix in suffix_replacements:
                    word_updated = word.replace(suffix, suffix_replacements[suffix])

            logger.warn("Removing suffix %s from word %s: %s" % (suffix, word, word_updated))
            word = word_updated
            break
    return word


def simplify_word(word):
    logger.warn(u"--------- Simplifying %s ---------" % (word))

    original_word = word

    # simple singularlize:
    if word.endswith('s') and word[0:-1] in dictionary:
        logger.warn("Simple desingularization returns valid word %s" % (word[0:-1]))
        return word[0:-1]

    word = replace_suffix(word)
    if word in dictionary:
        logger.warn("First round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word)
    if word in dictionary:
        logger.warn("First round prefix replaced to get valid word %s" % (word))
        return word

    # simple singularlize:
    if word.endswith('s'):
        word = word[0:-1]
        if word in dictionary:
            return word

    word = replace_suffix(word)
    if word in dictionary:
        logger.warn("Second round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word)
    if word in dictionary:
        logger.warn("Second round prefix replaced to get valid word %s" % (word))
        return word

    # simple singularlize:
    if word.endswith('s'):
        word = word[0:-1]
        if word in dictionary:
            return word

    word = replace_suffix(word)
    if word in dictionary:
        logger.warn("Third round suffix replaced to get valid word %s" % (word))
        return word

    word = replace_prefix(word)
    if word in dictionary:
        logger.warn("Third round prefix replaced to get valid word %s" % (word))
        return word

    lemmatized = lmtzr.lemmatize(word)
    if lemmatized in dictionary:
        logger.warn("Lemmatizer returned valid word %s" % (lemmatized))
        return lemmatized

    stemmed = snowball_stemmer.stem(word)
    if stemmed in dictionary:
        logger.warn("Stemmer returned valid word %s" % (stemmed))
        return stemmed

    logger.warn("No simplified version found, return original %s" % (original_word))
    return original_word


def get_misspelled_words(raw_text, language, custom_known_words=[]):

    # if language != 'en':
    #     return True, 'Language "%s" not supported' % (language)
    spell = SpellChecker(language=language, distance=1)

    logger.debug("raw_text:")
    logger.debug(raw_text)

    # Replace fancy typigraphic characters like curly quotes and em dashes
    typographic_translation_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”–-—⁃…•∙", u"'''\"\"----.--")])
    typography_removed = raw_text.translate(typographic_translation_table)
    hyphens_removed = typography_removed.replace("-", " ").replace("/", " ")
    newlines_removed = hyphens_removed.replace("\n", " ").replace("\r", " ")

    # Remove email addresses
    emails_removed = re.sub(r"\S*@\S*\s?", "", newlines_removed)
    hashes_removed = re.sub(r"#(\w+)", "", emails_removed)

    contractions_removed = contractions.fix(hashes_removed)
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
        simplified_word = simplify_word(word)
        if simplified_word not in dictionary:
            misspelled.append(simplified_word)

    logger.debug("misspelled:")
    logger.debug(misspelled)

    return misspelled
