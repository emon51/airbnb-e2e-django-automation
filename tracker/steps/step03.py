#step03.py
import random
import time
from tracker.services import save_result, get_state, set_state

WHEN_FIELD_SELECTORS = [
    '[data-testid="structured-search-input-field-split-dates-0"]',
    '[data-testid="structured-search-input-field-dates-button"]',
    'button[aria-label*="check in" i]',
    'button[aria-label*="dates" i]',
]

NEXT_MONTH_SELECTORS = [
    'button[aria-label*="Move forward" i]',
    'button[aria-label*="next month" i]',
    'button[aria-label*="forward" i]',
    'button[aria-label*="Next" i]',
]


def _picker_is_open(page) -> bool:
    """Check if calendar date picker is currently visible."""
    try:
        return bool(page.evaluate("""() => {
            const nextBtns = [...document.querySelectorAll(
                'button[aria-label*="Move forward" i], button[aria-label*="next month" i]'
            )].filter(el => el.offsetParent !== null);
            const dayBtns = [...document.querySelectorAll(
                'button[aria-label], table button, div[role="dialog"] button'
            )].filter(el => {
                const r = el.getBoundingClientRect();
                if (!r || r.width <= 0 || r.height <= 0) return false;
                if (el.hasAttribute('disabled')) return false;
                const text = (el.innerText || '').trim();
                return /^\\d{1,2}$/.test(text);
            });
            return nextBtns.length > 0 || dayBtns.length >= 8;
        }"""))
    except Exception:
        return False


def _open_date_picker(page) -> None:
    """Click the When/Add dates field to open the date picker."""
    # First expand the search bar by clicking query field
    try:
        page.get_by_test_id('structured-search-input-field-query').click()
        time.sleep(1.5)
        page.keyboard.press('Escape')
        time.sleep(0.5)
    except Exception:
        pass

    for sel in WHEN_FIELD_SELECTORS:
        try:
            el = page.query_selector(sel)
            if el and el.is_visible():
                el.click()
                print(f"  Clicked date field via: {sel}")
                time.sleep(1.5)
                return
        except Exception:
            continue

    # JS fallback
    try:
        page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('div, button, span'));
            const el = els.find(e =>
                ((e.innerText || '').toLowerCase().includes('add dates') ||
                 (e.getAttribute('aria-label') || '').toLowerCase().includes('check in') ||
                 (e.getAttribute('aria-label') || '').toLowerCase().includes('dates')) &&
                e.offsetParent !== null
            );
            if (el) el.click();
        }""")
        time.sleep(1.5)
    except Exception:
        pass


def _ensure_picker_open(page, attempts=4) -> bool:
    """Try to open date picker with multiple attempts."""
    for _ in range(attempts):
        if _picker_is_open(page):
            return True
        _open_date_picker(page)
        time.sleep(1.0)
        if _picker_is_open(page):
            return True
    return False


def _click_next_month(page) -> bool:
    """Click the next month button."""
    for sel in NEXT_MONTH_SELECTORS:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=500):
                loc.click(timeout=1500)
                return True
        except Exception:
            continue

    try:
        clicked = page.evaluate("""() => {
            const btn = [...document.querySelectorAll('button')]
                .find(el =>
                    el.offsetParent !== null &&
                    /(move forward|next month|forward)/i.test(el.getAttribute('aria-label') || '')
                );
            if (btn) { btn.click(); return true; }
            return false;
        }""")
        return bool(clicked)
    except Exception:
        return False


def _get_day_buttons(page) -> list:
    """Return all visible enabled day buttons with coordinates."""
    try:
        return page.evaluate("""() => {
            const seen = new Set();
            const out = [];

            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                if (!r || r.width <= 0 || r.height <= 0) return false;
                const style = window.getComputedStyle(el);
                return style.display !== 'none' && style.visibility !== 'hidden';
            };

            const isEnabled = (el) => {
                if (!el) return false;
                if (el.hasAttribute('disabled')) return false;
                if ((el.getAttribute('aria-disabled') || '').toLowerCase() === 'true') return false;
                return true;
            };

            const candidates = [
                ...document.querySelectorAll(
                    'div[role="dialog"] button, table button, ' +
                    '[data-testid*="calendar"] button, ' +
                    'button[data-state--date-string]'
                )
            ];

            for (const el of candidates) {
                if (!isVisible(el) || !isEnabled(el)) continue;
                const text = (el.innerText || '').trim();
                if (!/^\\d{1,2}$/.test(text)) continue;
                const label = (el.getAttribute('aria-label') || '').trim();
                if (/(move forward|next month|previous|backward)/i.test(label)) continue;

                const r = el.getBoundingClientRect();
                const x = r.left + r.width / 2;
                const y = r.top + r.height / 2;
                const key = `${Math.round(x)}:${Math.round(y)}`;
                if (seen.has(key)) continue;
                seen.add(key);

                out.push({
                    label: label,
                    text: text,
                    x: x,
                    y: y,
                });
            }
            return out;
        }""")
    except Exception:
        return []


def _read_month_label(page) -> str:
    """Read the visible month/year label from calendar."""
    for sel in ['h2[aria-live="polite"]', '[data-testid="calendar-heading"]', 'h2']:
        try:
            for el in page.query_selector_all(sel):
                text = (el.inner_text() or '').strip()
                if any(m in text for m in [
                    'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                    'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                ]):
                    return text
        except Exception:
            continue
    return ''


def run(page):
    """Step 03: Open date picker, navigate months, select check-in and check-out."""

    time.sleep(2)
    country = get_state('country')
    print(f"[Step 03] Country: '{country}'")

    required_next_clicks = random.randint(3, 8)
    next_clicks_done = 0
    month_label = ''
    checkin_label = ''
    checkout_label = ''

    # Ensure picker is open
    picker_visible = _ensure_picker_open(page, attempts=4)
    if not picker_visible:
        save_result('Step 03 - Date Picker Open', page.url, False,
                    'Calendar could not be opened')
        raise AssertionError("Date picker could not be opened")

    print("[Step 03] Calendar is open")
    save_result('Step 03 - Date Picker Open', page.url, True,
                f'Calendar opened | Country: {country}')

    # Navigate forward required months
    for i in range(required_next_clicks):
        if _click_next_month(page):
            next_clicks_done += 1
            print(f"  Month {next_clicks_done}/{required_next_clicks} navigated")
            time.sleep(0.8)
        else:
            # Reopen picker if it closed
            _ensure_picker_open(page, attempts=2)

    month_label = _read_month_label(page)
    print(f"[Step 03] Visible month: {month_label} | Navigated: {next_clicks_done}/{required_next_clicks}")

    # Get day buttons
    days = _get_day_buttons(page)
    print(f"[Step 03] Day buttons found: {len(days)}")
    assert len(days) >= 2, "Not enough day buttons found"

    # Select check-in — pick from first half
    checkin_index = random.randint(0, max(0, len(days) // 2 - 1))
    checkin_candidate = days[checkin_index]
    checkin_label = checkin_candidate.get('label') or checkin_candidate.get('text', '')
    page.mouse.click(float(checkin_candidate['x']), float(checkin_candidate['y']))
    print(f"[Step 03] Check-in clicked: {checkin_label}")
    time.sleep(1.0)

    # Ensure picker still open for checkout
    _ensure_picker_open(page, attempts=2)

    # Refresh day buttons after check-in click
    days = _get_day_buttons(page)
    checkout_index = random.randint(
        checkin_index + 1,
        min(checkin_index + 10, len(days) - 1)
    )
    checkout_candidate = days[checkout_index]
    checkout_label = checkout_candidate.get('label') or checkout_candidate.get('text', '')
    page.mouse.click(float(checkout_candidate['x']), float(checkout_candidate['y']))
    print(f"[Step 03] Check-out clicked: {checkout_label}")
    time.sleep(1.0)

    set_state('checkin', checkin_label)
    set_state('checkout', checkout_label)
    set_state('month_label', month_label)

    save_result(
        'Step 03 - Date Picker',
        page.url, True,
        f'Country: {country} | Month: {month_label} | '
        f'Check-in: {checkin_label} | Check-out: {checkout_label} | '
        f'Months navigated: {next_clicks_done}/{required_next_clicks}',
    )
    print(f"[Step 03] Done — Check-in: {checkin_label} | Check-out: {checkout_label}")
    return checkin_label, checkout_label