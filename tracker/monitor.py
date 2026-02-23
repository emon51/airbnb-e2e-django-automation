from tracker.models import ConsoleLog, NetworkLog


def attach_console_listener(page):
    """Capture all browser console messages and save to DB."""

    def handle_console(msg):
        try:
            ConsoleLog.objects.create(
                level=msg.type,
                message=msg.text,
                url=page.url,
            )
        except Exception as e:
            print(f"  [Console monitor error] {e}")

    page.on('console', handle_console)


def attach_network_listener(page):
    """Capture all network responses and save to DB."""

    def handle_response(response):
        try:
            NetworkLog.objects.create(
                method=response.request.method,
                url=response.url[:2000],
                status=response.status,
                resource_type=response.request.resource_type,
            )
        except Exception as e:
            print(f"  [Network monitor error] {e}")

    page.on('response', handle_response)