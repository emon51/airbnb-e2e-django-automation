# from tracker.models import Result


# def attach_console_listener(page):
#     """Capture browser console messages and save to DB."""
#     def handle_console(msg):
#         try:
#             Result.objects.create(
#                 test_case='Console Log',
#                 url=page.url,
#                 passed=msg.type not in ('error', 'warning'),
#                 comment=f'[{msg.type}] {msg.text}',
#             )
#         except Exception:
#             pass
#     page.on('console', handle_console)


# def attach_network_listener(page):
#     """Capture network responses and save to DB."""
#     def handle_response(response):
#         try:
#             passed = 200 <= response.status < 400
#             Result.objects.create(
#                 test_case='Network Request',
#                 url=response.url[:2000],
#                 passed=passed,
#                 comment=f'{response.request.method} {response.status} {response.request.resource_type}',
#             )
#         except Exception:
#             pass
#     page.on('response', handle_response)



def attach_console_listener(page):
    """Console monitoring — logging disabled."""
    pass


def attach_network_listener(page):
    """Network monitoring — logging disabled."""
    pass