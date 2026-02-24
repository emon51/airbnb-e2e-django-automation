from django.core.management.base import BaseCommand
from playwright.sync_api import sync_playwright
from tracker.steps import step01, step02, step03, step04, step05, step06
from tracker.monitor import attach_console_listener, attach_network_listener


class Command(BaseCommand):
    help = 'Run Airbnb end-to-end automation'

    def handle(self, *args, **kwargs):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            attach_console_listener(page)
            attach_network_listener(page)

            try:
                step01.run(page)
                step03.run(page)
                step04.run(page)
                step05.run(page)
                step06.run(page)
            finally:
                browser.close()

        self.stdout.write(self.style.SUCCESS('Automation complete'))