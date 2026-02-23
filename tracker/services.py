import os
from tracker.models import TestResult


SCREENSHOT_DIR = 'screenshots'


def save_result(test_case, url, passed, comment='', screenshot_path=''):
    """Save a test case result to the database."""
    result = TestResult(
        test_case=test_case,
        url=url,
        passed=passed,
        comment=comment,
    )
    if screenshot_path:
        result.screenshot = screenshot_path
    result.save()
    return result


def take_screenshot(page, name):
    """Take a full-page screenshot and return its relative path."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    page.screenshot(path=path, full_page=True)
    return path