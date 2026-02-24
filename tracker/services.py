import os
from django.conf import settings
from tracker.models import Result

SCREENSHOT_DIR = os.path.join(settings.BASE_DIR, 'screenshots')

# In-memory state shared across steps within the same process run
_state = {}


def set_state(key: str, value: str):
    """Save state in memory for use across steps in same run."""
    _state[key] = value


def get_state(key: str) -> str:
    """Get state saved during this run."""
    return _state.get(key, '')


def take_screenshot(page, name: str) -> str:
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    filename = f"{name}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)
    page.screenshot(path=filepath, full_page=True)
    return filename


def save_result(test_case: str, url: str, passed: bool, comment: str = '', screenshot: str = '') -> Result:
    return Result.objects.create(
        test_case=test_case,
        url=url,
        passed=passed,
        comment=comment,
        screenshot=screenshot,
    )