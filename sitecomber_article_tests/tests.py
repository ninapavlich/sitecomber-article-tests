import logging
import json

from sitecomber.apps.shared.interfaces import BaseSiteTest

from .utils.article import is_reader_view_enabled, contains_placeholder_text, get_article_readtime
from .utils.spelling import check_spelling

logger = logging.getLogger('django')


def should_test_page(page):
    if not page.last_status_code:
        return False
    if not page.is_internal:
        return False
    if page.last_content_type and 'text/html' not in page.last_content_type.lower():
        return False
    return True


class ReaderViewTest(BaseSiteTest):
    """
    Determins if the page has a structured article
    Uses library https://github.com/codelucas/newspaper/
    """

    def get_description_html(self):

        return """<p>Determins if the page has a structured article (with a title, body text,
    author, main image and publication date) and is therefore optimized for
    reader viewers such as Pocket, Instapaper or browser reader view.</p>
    <p>This test uses the Python library <a href="https://github.com/codelucas/newspaper/">Newspaper3k</a>
    to extract the article content.</p>
        """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            reader_view_enabled, status, message, data = is_reader_view_enabled(page, self.settings)

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            try:
                r.data = json.dumps(data, sort_keys=True, indent=2)
            except Exception as e:
                logger.error(u"Error dumping JSON data: %s: %s" % (data, e))
            r.save()


class PlaceholderTextTest(BaseSiteTest):
    """
    This test looks for lorem or ipsum or tk in main article body and title
    """

    @property
    def placeholder_words(self):
        return ['lorem', 'ipsum'] if 'placeholder_words' not in self.settings else self.settings['placeholder_words']

    def get_description_html(self):

        return """<p>This test looks for the placeholder words \"%s\" in the main article body or title. </p>
            <small>To adjust which words are searched for, go to the Site configuration
            settings and scroll down to the "PlaceholderTextTest" section.
            Custom words should be entered as a JSON list, in this format:
            <pre>
              {
                "placeholder_words": [
                  "lorem",
                  "todo",
                  "tbd",
                ]
              }
            </pre></small></p>
        """ % ('", "'.join(self.placeholder_words))

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            placeholder_text, message, data = contains_placeholder_text(page, self.settings, self.placeholder_words)
            status = PageTestResult.STATUS_SUCCESS if not placeholder_text else PageTestResult.STATUS_ERROR

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            try:
                r.data = json.dumps(data, sort_keys=True, indent=2)
            except Exception as e:
                logger.error(u"Error dumping JSON data: %s: %s" % (data, e))
            r.save()


class ArticleReadTimeInfo(BaseSiteTest):
    """
    Determines approximate read time based on library
    https://github.com/alanhamlett/readtime
    """

    def get_description_html(self):

        return """<p>This test returns approximate read time based on <a href="https://help.medium.com/hc/en-us/articles/214991667-Read-time">Medium's read time forumula</a> of roughly 265 WPM.</p>
    <p>See the <a href="https://github.com/alanhamlett/readtime">readtime library</a> for more details.</p>
        """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            message, data = get_article_readtime(page, self.settings)

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = PageTestResult.STATUS_INFO
            try:
                r.data = json.dumps(data, sort_keys=True, indent=2)
            except Exception as e:
                logger.error(u"Error dumping JSON data: %s: %s" % (data, e))
            r.save()


class SpellCheckTest(BaseSiteTest):
    """
    Check spelling using pyspellchecker
    See https://github.com/barrust/pyspellchecker
    """

    def get_description_html(self):

        return """
            <p>This test checks spelling in the main article title and body text.</p>

            <p><small>If a word is caught that shouldn't be, it may be that this
            word is simply not in the Python NLTK corpus dictionary.</small></p>

            <p><small>To add a word to the custom dictionary, go to the Site
            configuration settings and scroll down to the "SpellCheckTest"
            section. Custom words should be entered as a JSON list, in this format:
            <pre>
              {
                "known_words": [
                  "swole",
                  "cheesemonger",
                  "gadzooks",
                ]
              }
            </pre></small></p>
        """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult
        if should_test_page(page):

            contains_misspellings, message, data = check_spelling(page, self.settings)
            status = PageTestResult.STATUS_SUCCESS if not contains_misspellings else PageTestResult.STATUS_ERROR

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            try:
                r.data = json.dumps(data, sort_keys=True, indent=2)
            except Exception as e:
                logger.error(u"Error dumping JSON data: %s: %s" % (data, e))
            r.save()
