from sitecomber.apps.shared.interfaces import BaseSiteTest


from .utils import is_reader_view_enabled


class ReaderViewTest(BaseSiteTest):
    """
    Is this page optimized for reader view?
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if page.latest_request and page.latest_request.response and page.is_internal:

            reader_view_enabled = is_reader_view_enabled(page.latest_request.response.text_content)
            status = PageTestResult.STATUS_SUCCESS if reader_view_enabled == 200 else PageTestResult.STATUS_ERROR
            message = 'Okay' if reader_view_enabled == 200 else 'Reader view not found on %s' % (page.url)

            r, created = PageTestResult.objects.get_or_create(
                page=page,
                test=self.class_path
            )
            r.message = message
            r.status = status
            r.save()


class PlaceholderTextTest(BaseSiteTest):
    """
    Looks for lorem or ipsum or tk
    """

    def on_page_parsed(self, page):
        from sitecomber.apps.results.models import PageTestResult

        if page.latest_request and page.latest_request.response and page.is_internal:

            if is_reader_view_enabled(page.latest_request.response.text_content):
