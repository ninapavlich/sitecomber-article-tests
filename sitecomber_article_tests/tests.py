from sitecomber.apps.shared.interfaces import BaseSiteTest


from .utils import is_reader_view_enabled, contains_placeholder_text


class ReaderViewTest(BaseSiteTest):
    """
    Is this page optimized for reader view?
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
    Looks for lorem or ipsum or tk
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
