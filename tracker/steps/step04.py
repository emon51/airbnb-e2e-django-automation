import random
from tracker.services import save_result, take_screenshot


GUEST_TYPES = [
    'Adults',
    'Children',
    'Infants',
    'Pets',
]


def _increment_guest(page, label, count):
    """Click the + button for a given guest type a number of times."""
    increase_btn = page.locator(f'[data-testid="stepper-{label}-increase-button"]')
    for _ in range(count):
        increase_btn.click()
        page.wait_for_timeout(300)


def run(page):
    """Step 04: Open guest picker, select random guests, and click search."""

    # Click the guest input field
    guest_field = page.locator('[data-testid="structured-search-input-field-guests-button"]')
    guest_field.wait_for(state='visible', timeout=10000)
    guest_field.click()
    page.wait_for_timeout(1000)

    # Verify guest popup is open
    guest_popup = page.locator('[data-testid="structured-search-input-field-guests-button"]')
    assert guest_popup.is_visible(), "Guest picker did not open"

    take_screenshot(page, 'step04_guest_picker_open')

    # Must add at least 1 adult first (Airbnb requires it)
    adult_count = random.randint(1, 3)
    _increment_guest(page, 'adults', adult_count)

    # Randomly add children, infants, pets (0 to 2 each)
    children_count = random.randint(0, 2)
    infants_count = random.randint(0, 2)
    pets_count = random.randint(0, 2)

    if children_count:
        _increment_guest(page, 'children', children_count)
    if infants_count:
        _increment_guest(page, 'infants', infants_count)
    if pets_count:
        _increment_guest(page, 'pets', pets_count)

    page.wait_for_timeout(500)
    take_screenshot(page, 'step04_guests_selected')

    summary = (
        f'Adults: {adult_count} | Children: {children_count} | '
        f'Infants: {infants_count} | Pets: {pets_count}'
    )
    save_result('Guest Picker Interaction', page.url, True, summary)

    # Click search button
    search_btn = page.locator('[data-testid="structured-search-input-search-button"]')
    search_btn.wait_for(state='visible', timeout=5000)
    search_btn.click()
    page.wait_for_timeout(3000)

    take_screenshot(page, 'step04_search_clicked')
    save_result('Search Button Clicked', page.url, True, f'Search triggered with: {summary}')

    print(f"[Step 04] Done — {summary}")