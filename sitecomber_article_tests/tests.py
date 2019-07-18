from sitecomber.apps.shared.interfaces import BaseSiteTest


from .utils import is_reader_view_enabled, contains_placeholder_text, get_article_readtime, check_spelling


class ReaderViewTest(BaseSiteTest):
    """
    Is this page optimized for reader view?
    See https://github.com/codelucas/newspaper/
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if page.latest_request and page.latest_request.response and page.is_internal:

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

        if page.latest_request and page.latest_request.response and page.is_internal:

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

        if page.latest_request and page.latest_request.response and page.is_internal:

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
        if page.latest_request and page.latest_request.response and page.is_internal:

            contains_misspellings, message = check_spelling(page, self.settings)
            status = PageTestResult.STATUS_SUCCESS if not contains_misspellings else PageTestResult.STATUS_ERROR

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            r.save()
