import logging

from newspaper import Article
from newspaper.utils import get_available_languages

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

    placeholder_strings = ['lorem', 'ipsum', 'tk']

    if article.text:
        text_lower = article.text.lower()
        for placeholder_string in placeholder_strings:
            if placeholder_string in text_lower:
                return True, u"Found placeholder string %s" % (placeholder_string)

    message = 'No placeholder text "%s" found.' % ('", "'.join(placeholder_strings))
    return False, message
