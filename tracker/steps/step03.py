import random
from tracker.services import save_result, take_screenshot


def run(page):
    """Step 03: Interact with date picker — select check-in and check-out dates."""

    # Verify date picker is visible after suggestion selection
    date_picker = page.locator('[data-testid="structured-search-input-field-split-dates-0"]')
    date_picker.wait_for(state='visible', timeout=10000)
    date_picker.click()
    page.wait_for_timeout(1000)

    # Click next month randomly between 3 and 8 times
    next_month_clicks = random.randint(3, 8)
    for _ in range(next_month_clicks):
        page.locator('[aria-label="Move forward to switch to the next month."]').click()
        page.wait_for_timeout(500)

    take_screenshot(page, 'step03_date_picker_navigated')

    # Get all available (not disabled) day buttons
    available_days = page.locator('[data-testid="calendar-day-button"]:not([disabled])').all()
    assert len(available_days) >= 2, "Not enough available dates"

    # Select check-in date (pick from first half of available days)
    checkin_index = random.randint(0, len(available_days) // 2 - 1)
    checkin_btn = available_days[checkin_index]
    checkin_label = checkin_btn.get_attribute('aria-label')
    checkin_btn.click()
    page.wait_for_timeout(1000)

    # Refresh available days and select checkout after check-in
    available_days = page.locator('[data-testid="calendar-day-button"]:not([disabled])').all()
    checkout_index = random.randint(checkin_index + 1, min(checkin_index + 10, len(available_days) - 1))
    checkout_btn = available_days[checkout_index]
    checkout_label = checkout_btn.get_attribute('aria-label')
    checkout_btn.click()
    page.wait_for_timeout(1000)

    take_screenshot(page, 'step03_dates_selected')
    save_result(
        'Date Picker Interaction',
        page.url,
        True,
        f'Check-in: {checkin_label} | Check-out: {checkout_label} | Next month clicks: {next_month_clicks}'
    )

    print(f"[Step 03] Done — Check-in: {checkin_label} | Check-out: {checkout_label}")
    return checkin_label, checkout_label