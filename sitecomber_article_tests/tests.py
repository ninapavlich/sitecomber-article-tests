from sitecomber.apps.shared.interfaces import BaseSiteTest


from .utils import is_reader_view_enabled, contains_placeholder_text, get_article_readtime, check_spelling


def should_test_page(page):
    if not page.latest_request:
        return False
    if not page.is_internal:
        return False
    if not page.latest_request.response:
        return False
    if 'text/html' not in page.latest_request.response.content_type.lower():
        return False
    return True


class ReaderViewTest(BaseSiteTest):
    """
    Is this page optimized for reader view?
    See https://github.com/codelucas/newspaper/
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            reader_view_enabled, status, message = is_reader_view_enabled(page, self.settings)

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            r.save()


class PlaceholderTextTest(BaseSiteTest):
    """
    Looks for lorem or ipsum or tk in main article body and title
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            placeholder_text, message = contains_placeholder_text(page, self.settings)
            status = PageTestResult.STATUS_SUCCESS if not placeholder_text else PageTestResult.STATUS_ERROR

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            r.save()


class ArticleReadTimeInfo(BaseSiteTest):
    """
    Returns approximate read time based on 265WPM estimate
    See https://pypi.org/project/readtime/
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if should_test_page(page):

            message = get_article_readtime(page, self.settings)

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = PageTestResult.STATUS_INFO
            r.save()


class SpellCheckTest(BaseSiteTest):
    """
    Check spelling using pyspellchecker
    See https://github.com/barrust/pyspellchecker
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult
        if should_test_page(page):

            contains_misspellings, message = check_spelling(page, self.settings)
            status = PageTestResult.STATUS_SUCCESS if not contains_misspellings else PageTestResult.STATUS_ERROR

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            r.save()
