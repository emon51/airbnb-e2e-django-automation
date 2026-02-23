import os
import random
from tracker.services import save_result, take_screenshot

AIRBNB_URL = os.getenv('AIRBNB_URL', 'https://www.airbnb.com/')

TOP_20_COUNTRIES = [
    'United States', 'China', 'India', 'Brazil', 'Russia',
    'Indonesia', 'Pakistan', 'Nigeria', 'Bangladesh', 'Ethiopia',
    'Mexico', 'Japan', 'Philippines', 'Egypt', 'DR Congo',
    'Vietnam', 'Iran', 'Turkey', 'Germany', 'Thailand',
]


def run(page):
    """Step 01: Land on Airbnb, clear storage, search a random country."""

    # Navigate and wait for DOM only — Airbnb has continuous background requests
    page.goto(AIRBNB_URL, wait_until='domcontentloaded')
    page.wait_for_timeout(3000)

    # Clear storage and cookies after page load
    page.context.clear_cookies()
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

    # Close any popup/modal if present
    try:
        close_btn = page.locator('[aria-label="Close"]').first
        if close_btn.is_visible():
            close_btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass

    # Confirm homepage loaded
    assert 'airbnb' in page.url.lower(), "Homepage did not load"
    take_screenshot(page, 'step01_homepage')
    save_result('Homepage Load', page.url, True, 'Airbnb homepage loaded successfully')

    # Click search field
    page.locator('[data-testid="structured-search-input-field-query"]').first.click()
    page.wait_for_timeout(1000)

    # Pick a random country and type it
    country = random.choice(TOP_20_COUNTRIES)
    page.keyboard.type(country, delay=100)
    page.wait_for_timeout(2000)

    take_screenshot(page, 'step01_search_typed')
    save_result('Search Input', page.url, True, f'Typed country: {country}')

    print(f"[Step 01] Done — searched for: {country}")
    return country