import logging
import re
from string import punctuation

import nltk.data
from nltk.corpus import stopwords
# from nltk.stem.wordnet import WordNetLemmatizer
# from nltk.stem import SnowballStemmer

import contractions

from spellchecker import SpellChecker

from .article import get_article
from .dictionary import extended_dictionary


logger = logging.getLogger('django')


def check_spelling(page, settings):
    # Validate that this is for English; currently only English is supported
    language = 'en' if 'lang' not in settings else settings['lang']

    article = get_article(page, settings)
    custom_known_words = [] if 'known_words' not in settings else settings['known_words']

    dictionary = set(list(extended_dictionary) + list(custom_known_words))

    if article.text:
        raw_text = u'%s. %s' % (article.title, article.text)
        misspelled = get_misspelled_words(raw_text, language, dictionary)
        found_misspellings = len(misspelled) > 0
        message = "No misspellings found" if not found_misspellings else u'Found %s misspelling(s): "%s"' % (len(misspelled), '", "'.join(misspelled))
        return found_misspellings, message, {'misspelled_words': misspelled}

    return False, 'No article found', {}

suffixes = [
    {'able': ''},
    {'acy': ''},
    {'al': ''},
    {'ance': ''},
    {'ate': ''},
    {'bility': ''},
    {'bility': 'ble'},
    {'bio': ''},
    {'dom': ''},
    {'ed': ''},
    {'ed': 'e'},
    {'ee': ''},
    {'en': ''},
    {'en': 'e'},
    {'ence': ''},
    {'ence': 'e'},
    {'er': ''},
    {'er': 'e'},
    {'erizer': ''},
    {'es': ''},
    {'es': 'e'},
    {'esque': ''},
    {'est': ''},
    {'ful': ''},
    {'fy': ''},
    {'hood': ''},
    {'ible': ''},
    {'ic': ''},
    {'ical': ''},
    {'ied': ''},
    {'ied': 'y'},
    {'ier': ''},
    {'ier': 'y'},
    {'ies': ''},
    {'ies': 'y'},
    {'iest': ''},
    {'iest': 'y'},
    {'ify': ''},
    {'ily': ''},
    {'iness': ''},
    {'iness': 'y'},
    {'ing': ''},
    {'ing': 'e'},
    {'ious': ''},
    {'ise': ''},
    {'ish': ''},
    {'ism': ''},
    {'ist': ''},
    {'ity': ''},
    {'ity': 'y'},
    {'ive': ''},
    {'ize': ''},
    {'izer': ''},
    {'less': ''},
    {'like': ''},
    {'long': ''},
    {'ly': ''},
    {'mate': ''},
    {'ment': ''},
    {'ness': ''},
    {'ologist': ''},
    {'ologist': 'ology'},
    {'ous': ''},
    {'ped': ''},
    {'pping': ''},
    {'pping': 'p'},
    {'red': ''},
    {'red': 're'},
    {'s': ''},
    {'sion': ''},
    {'tion': ''},
    {'tion': 'te'},
    {'tize': ''},
    {'tize': 'ty'},
    {'tize': 't'},
    {'tted': ''},
    {'tted': 't'},
    {'ty': ''},
    {'ward': ''},
    {'wards': ''},
    {'wide': ''},
    {'wise': ''},
    {'worthy': ''},
    {'y': ''}
]


prefixes = [
    {'ante': ''},
    {'anti': ''},
    {'auto': ''},
    {'bi': ''},
    {'bio': ''},
    {'bis': ''},
    {'co': ''},
    {'de': ''},
    {'dis': ''},
    {'en': ''},
    {'ex': ''},
    {'extra': ''},
    {'hyper': ''},
    {'ig': ''},
    {'im': ''},
    {'in': ''},
    {'inter': ''},
    {'ir': ''},
    {'macro': ''},
    {'mal': ''},
    {'mega': ''},
    {'micro': ''},
    {'mini': ''},
    {'mis': ''},
    {'mono': ''},
    {'multi': ''},
    {'neo': ''},
    {'neuro': ''},
    {'non': ''},
    {'omni': ''},
    {'over': ''},
    {'penta': ''},
    {'per': ''},
    {'poly': ''},
    {'post': ''},
    {'pre': ''},
    {'pro': ''},
    {'quad': ''},
    {'re': ''},
    {'retro': ''},
    {'semi': ''},
    {'socio': ''},
    {'sub': ''},
    {'super': ''},
    {'tran': ''},
    {'tri': ''},
    {'un': ''},
    {'under': ''},
    {'uni': ''}
]
# Sort prefixes and suffixes from longest to shortest
suffixes.sort(key=lambda s: len(next(iter(s))))
suffixes.reverse()
prefixes.sort(key=lambda s: len(next(iter(s))))
prefixes.reverse()

stop_words = set(stopwords.words('english'))


def is_in_dictionary(word, dictionary):
    if len(word) == 1:
        if word.lower() == 'a' or word.lower() == 'i' or word.lower() == 'o':
            return True
    else:
        return (word in dictionary)


def get_simplification_options(word):
    output = []

    for prefix_item in prefixes:
        prefix = next(iter(prefix_item))
        if word.startswith(prefix):
            output.append({
                'type': 'prefix',
                'search': prefix,
                'replace': prefix_item[prefix]
            })

    for suffix_item in suffixes:
        suffix = next(iter(suffix_item))
        if word.endswith(suffix):
            output.append({
                'type': 'suffix',
                'search': suffix,
                'replace': suffix_item[suffix]
            })

    return output


def apply_simplification(word, simplification):
    if simplification['type'] == 'prefix':
        if word.startswith(simplification['search']):
            word = simplification['replace'] + word[len(simplification['search']):]

    if simplification['type'] == 'suffix':
        if word.endswith(simplification['search']):
            word = word[:-len(simplification['search'])] + simplification['replace']

    return word


def simplify_word(word, dictionary, debug=False):
    log_level = logging.WARNING if debug else logging.DEBUG

    logger.log(log_level, u"\n--------- Simplifying %s ---------" % (word))

    possible_simplifications = get_simplification_options(word)
    logger.log(log_level, "Possible simplifications: %s " % (possible_simplifications))

    if len(possible_simplifications) == 0:
        logger.log(log_level, "No more simplification options found, returning %s" % (word))
        return word

    for simplification in possible_simplifications:

        applied = apply_simplification(word, simplification)
        logger.log(log_level, "Applied simplification %s replaced --> %s" % (simplification, applied))
        if is_in_dictionary(applied, dictionary):
            logger.log(log_level, "Simplification yielded valid word %s" % (applied))
            return applied

        else:
            drilled_down = simplify_word(applied, dictionary, debug)
            if is_in_dictionary(drilled_down, dictionary):
                logger.log(log_level, "Drilled down yielded valid word %s" % (drilled_down))
                return drilled_down
    return word


def remove_emails(input):
    return re.sub(r"\S*@\S*\s?", " ", input)


def remove_hashes(input):
    return re.sub(r"#(\w+)", " ", input)


def remove_phonenumbers(input):
    # TODO
    # intl_removed = re.sub(r'(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+', ' ', input)
    # intl_removed = input
    intl_removed = re.sub(r"(\d{1,3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", " ", input)
    us_removed = re.sub(r"(\d{1,3}[-\.\s]??\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", " ", intl_removed)

    return us_removed


def remove_urls(input):
    # return re.sub(r'\s*(?:https?://)?\S*\.[A-Za-z]{2,5}\s*', " ", input)
    removed_full_links = re.sub(r'(http|https|ftp|telnet):\/\/[\w\-_]+(\.[\w\-_]+)+([\w\-\.,@?^=%&amp;:/~\+#]*[\w\-\@?^=%&amp;/~\+#])?', " ", input)
    remove_partial_links = re.sub(r"([\w\.]+\.(?:com|org|net|us|co|edu|gov|uk)[^,\s]*)", " ", removed_full_links)
    remove_mailtos = re.sub(r'((mailto\:|(news|(ht|f)tp(s?))\://){1}\S+)', " ", remove_partial_links)
    ips_removed = re.sub(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", " ", remove_mailtos)
    intl_removed = re.sub(r'(tel):(\+[0-9]+\s*)?(\([0-9]+\))?[\s0-9\-]+[0-9]+', ' ', ips_removed)
    us_removed = re.sub(r"(tel):(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})", " ", intl_removed)
    filenames_removed = re.sub(r"([\w\d\-.]+\.(pdf|PDF|doc|DOC|docx|DOCX|zip|ZIP|xlsx|XLSX|csv|CSV))", " ", us_removed)
    return filenames_removed


def remove_acronyms(input):
    return re.sub(r"\b[A-Z\.]{2,}s?\b", "", input)


def get_misspelled_words(raw_text, language, dictionary, debug=False):
    log_level = logging.WARNING if debug else logging.DEBUG

    # if language != 'en':
    #     return True, 'Language "%s" not supported' % (language)
    spell = SpellChecker(language=language, distance=1)

    logger.log(log_level, ">> raw_text:")
    logger.log(log_level, raw_text)

    # Remove email addresses, hashes, urls, phone numbers...
    urls_removed = remove_urls(raw_text)
    emails_removed = remove_emails(urls_removed)
    hashes_removed = remove_hashes(emails_removed)
    phonenumbers_removed = remove_phonenumbers(hashes_removed)

    logger.log(log_level, ">> after email, hashes, urls, phone numbers removed:")
    logger.log(log_level, phonenumbers_removed)

    # Replace fancy typigraphic characters like curly quotes and em dashes
    typographic_translation_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´'“”–-—⁃‐…●•∙©", u"''''\"\"-----.----")])
    typography_removed = phonenumbers_removed.translate(typographic_translation_table)
    hyphens_removed = typography_removed.replace("-", " ").replace("/", " ")
    newlines_removed = hyphens_removed.replace("\n", " ").replace("\r", " ")

    logger.log(log_level, ">> after fancy typographic characters and newlines removed:")
    logger.log(log_level, newlines_removed)

    contractions_removed = contractions.fix(newlines_removed)
    possessives_removed = re.sub("\'s ", " ", contractions_removed)
    hyphens_removed = possessives_removed.replace("-", " ")
    acronyms_removed = remove_acronyms(hyphens_removed)
    whitespace_condensed = re.sub("[ \t]+", " ", acronyms_removed.replace(u'\u200b', ' '))

    logger.log(log_level, ">> after contractions, posessives, hyphens and acronyms removed:")
    logger.log(log_level, whitespace_condensed)

    # Split text into words
    check_words_raw = whitespace_condensed.split(' ')
    logger.log(log_level, ">> check_words_raw:")
    logger.log(log_level, check_words_raw)

    # Remove stopwords for faster processing
    stopwords_removed = [word for word in check_words_raw if (word.lower() not in stop_words)]
    logger.log(log_level, ">> stopwords_removed:")
    logger.log(log_level, stopwords_removed)

    # Remove any numbers and punctuation

    # This excludes a word with a number anywhere in it:
    # punctuation_removed = [word.strip(punctuation) for word in stopwords_removed if (word and not re.search('\d+', word))]
    punctuation_removed = [word.strip(punctuation) for word in stopwords_removed if (word and not word[0].isdigit())]

    logger.log(log_level, ">> punctuation_removed:")
    logger.log(log_level, punctuation_removed)

    remove_empty_words = [word for word in punctuation_removed if word]

    # Gather list of assumed proper nouns.
    # Assume anything capitalized in article is a local proper noun
    proper_nouns = []
    for word in remove_empty_words:
        if word[0].isupper() and not is_in_dictionary(simplify_word(word.lower(), dictionary), dictionary):
            proper_nouns.append(word.strip(punctuation))
    proper_nouns_lower = [word.lower() for word in proper_nouns]
    logger.log(log_level, ">> proper_nouns:")
    logger.log(log_level, proper_nouns)

    # Remove anything matching a proper noun from above
    remove_proper_nounds = [item for item in remove_empty_words if item.lower() not in proper_nouns_lower]

    # Reduce to unique set of words
    check_words = list(set(remove_proper_nounds))
    logger.log(log_level, ">> check_words:")
    logger.log(log_level, check_words)

    # First check the corpus dictionary:
    words_not_in_dict = [word for word in check_words if not is_in_dictionary(word.lower(), dictionary)]
    logger.log(log_level, ">> words_not_in_dict:")
    logger.log(log_level, words_not_in_dict)

    # Next use spelling library
    unknown = [item for item in list(spell.unknown(words_not_in_dict))]
    logger.log(log_level, ">> unknown:")
    logger.log(log_level, unknown)

    # Finally, removing prefix and suffixes to unearth a valid root word
    misspelled = []
    for word in unknown:
        simplified_word = simplify_word(word, dictionary)
        if not is_in_dictionary(simplified_word, dictionary):
            misspelled.append(simplified_word)

    logger.log(log_level, ">> misspelled:")
    logger.log(log_level, misspelled)

    return misspelled
