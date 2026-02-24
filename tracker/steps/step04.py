# Step04.py

import random
import time
from tracker.services import save_result, get_state, set_state

GUEST_FIELD_SELECTORS = [
    '[data-testid="structured-search-input-field-guests-button"]',
    'button[aria-label*="who" i]',
    'button[aria-label*="guests" i]',
    'button:has-text("Who")',
    'button:has-text("Add guests")',
]

STEPPER_INCREASE_SELECTORS = {
    'adults':   'button[data-testid="stepper-adults-increase-button"]',
    'children': 'button[data-testid="stepper-children-increase-button"]',
    'infants':  'button[data-testid="stepper-infants-increase-button"]',
    'pets':     'button[data-testid="stepper-pets-increase-button"]',
}

STEPPER_VALUE_SELECTORS = {
    'adults':   '[data-testid="stepper-adults-value"]',
    'children': '[data-testid="stepper-children-value"]',
    'infants':  '[data-testid="stepper-infants-value"]',
    'pets':     '[data-testid="stepper-pets-value"]',
}

SEARCH_BTN_SELECTORS = [
    '[data-testid="structured-search-input-search-button"]',
    'button[aria-label="Search"]',
    'button:has-text("Search")',
]


def _popup_is_open(page) -> bool:
    """Check if guest stepper popup is open."""
    try:
        return bool(page.evaluate("""() => {
            const selectors = [
                'button[data-testid="stepper-adults-increase-button"]',
                'button[data-testid="stepper-children-increase-button"]',
                '[data-testid="stepper-adults-value"]',
                '[data-testid="stepper-children-value"]',
            ];
            for (const sel of selectors) {
                const nodes = document.querySelectorAll(sel);
                for (const node of nodes) {
                    if (node.offsetParent !== null) return true;
                }
            }
            return false;
        }"""))
    except Exception:
        return False


def _open_guest_field(page) -> bool:
    """Click the Who/Add guests field to open the stepper popup."""

    # Try by testid first
    for sel in GUEST_FIELD_SELECTORS:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=500):
                loc.click(timeout=1500)
                time.sleep(0.5)
                if _popup_is_open(page):
                    print(f"  Guest field opened via: {sel}")
                    return True
        except Exception:
            continue

    # JS fallback — find Who/Add guests by text
    try:
        clicked = bool(page.evaluate("""() => {
            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                if (!r || r.width <= 0 || r.height <= 0) return false;
                const s = window.getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden';
            };
            const candidates = [...document.querySelectorAll(
                'button, div[role="button"], [role="button"]'
            )].filter(isVisible);
            const target = candidates.find(el => {
                const text = (el.innerText || el.textContent || '').trim().toLowerCase();
                return text.includes('who') || text.includes('add guests') || text.includes('guests');
            });
            if (!target) return false;
            target.click();
            return true;
        }"""))
        if clicked:
            time.sleep(0.5)
            if _popup_is_open(page):
                print("  Guest field opened via JS fallback")
                return True
    except Exception:
        pass

    return False


def _discover_available_stepper_keys(page) -> list:
    """Return list of guest category keys with visible enabled increase buttons."""
    try:
        keys = page.evaluate("""() => {
            const map = {
                adults:   'button[data-testid="stepper-adults-increase-button"]',
                children: 'button[data-testid="stepper-children-increase-button"]',
                infants:  'button[data-testid="stepper-infants-increase-button"]',
                pets:     'button[data-testid="stepper-pets-increase-button"]',
            };
            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                if (!r || r.width <= 0 || r.height <= 0) return false;
                const s = window.getComputedStyle(el);
                return s.display !== 'none' && s.visibility !== 'hidden';
            };
            const out = [];
            for (const [key, selector] of Object.entries(map)) {
                const nodes = [...document.querySelectorAll(selector)].filter(isVisible);
                const enabled = nodes.some(el =>
                    !el.hasAttribute('disabled') &&
                    (el.getAttribute('aria-disabled') || '').toLowerCase() !== 'true'
                );
                if (enabled) out.push(key);
            }
            return out;
        }""")
        if isinstance(keys, list):
            return [k for k in keys if k in STEPPER_INCREASE_SELECTORS]
    except Exception:
        pass
    return []


def _click_stepper_increase(page, key: str) -> bool:
    """Click the increase button for a guest category."""
    sel = STEPPER_INCREASE_SELECTORS.get(key)
    if not sel:
        return False
    try:
        loc = page.locator(sel).first
        if loc.is_visible(timeout=400) and not loc.is_disabled():
            loc.click(timeout=1200)
            return True
    except Exception:
        pass
    try:
        return bool(page.evaluate(f"""() => {{
            const el = document.querySelector('{sel}');
            if (!el || el.hasAttribute('disabled')) return false;
            if ((el.getAttribute('aria-disabled') || '').toLowerCase() === 'true') return false;
            el.click();
            return true;
        }}"""))
    except Exception:
        return False


def _read_stepper_values(page) -> dict:
    """Read current stepper values for all guest categories."""
    values = {'adults': 0, 'children': 0, 'infants': 0, 'pets': 0}
    for key, sel in STEPPER_VALUE_SELECTORS.items():
        try:
            num = page.evaluate(f"""() => {{
                const el = [...document.querySelectorAll('{sel}')]
                    .find(el => el.offsetParent !== null);
                if (!el) return null;
                const m = (el.textContent || '').match(/\\d+/);
                return m ? parseInt(m[0], 10) : null;
            }}""")
            if isinstance(num, int):
                values[key] = num
        except Exception:
            continue
    return values


def _get_guest_display(page) -> str:
    """Read the current guest count text from the guest field."""
    for sel in GUEST_FIELD_SELECTORS:
        try:
            el = page.query_selector(sel)
            if not el:
                continue
            text = (el.inner_text() or '').strip()
            if text:
                return text
        except Exception:
            continue
    try:
        return page.evaluate("""() => {
            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return !!r && r.width > 0 && r.height > 0;
            };
            const nodes = [...document.querySelectorAll(
                '[data-testid*="guests"], [role="button"][aria-expanded]'
            )].filter(isVisible);
            for (const el of nodes) {
                const t = (el.innerText || el.textContent || '').trim();
                if (t && t.toLowerCase().includes('guest')) return t;
            }
            return '';
        }""") or ''
    except Exception:
        return ''


def _click_search(page) -> bool:
    """Click the Search button."""
    for sel in SEARCH_BTN_SELECTORS:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=500):
                loc.click(timeout=1500)
                print(f"  Search clicked via: {sel}")
                return True
        except Exception:
            continue

    # JS fallback
    try:
        clicked = bool(page.evaluate("""() => {
            const isVisible = (el) => {
                if (!el) return false;
                const r = el.getBoundingClientRect();
                return !!r && r.width > 0 && r.height > 0;
            };
            const candidates = [
                ...document.querySelectorAll(
                    '[data-testid="structured-search-input-search-button"], button, [role="button"]'
                )
            ].filter(isVisible);
            for (const el of candidates) {
                const text = (el.innerText || el.textContent || '').trim().toLowerCase();
                if (text === 'search' || text.startsWith('search')) {
                    el.click();
                    return true;
                }
            }
            return false;
        }"""))
        if clicked:
            print("  Search clicked via JS fallback")
        return clicked
    except Exception:
        return False


def run(page):
    """Step 04: Open guest picker, select random guests, click search."""

    time.sleep(1)
    country = get_state('country')
    checkin = get_state('checkin')
    checkout = get_state('checkout')
    print(f"[Step 04] Country: {country} | Check-in: {checkin} | Check-out: {checkout}")

    # Open guest field
    guest_click_ok = _open_guest_field(page)

    # Wait for popup to open with retries
    popup_visible = False
    for attempt in range(8):
        if _popup_is_open(page):
            popup_visible = True
            break
        print(f"  Waiting for guest popup... attempt {attempt + 1}")
        if attempt < 7:
            _open_guest_field(page)
        time.sleep(1.0)

    if not popup_visible:
        save_result('Step 04 - Guest Picker', page.url, False,
                    f'Guest popup did not open. Click success: {guest_click_ok}')
        raise AssertionError("Guest picker popup did not open")

    print("[Step 04] Guest popup is open")

    # Discover available stepper keys
    available_keys = _discover_available_stepper_keys(page)
    print(f"  Available steppers: {available_keys}")

    if not available_keys:
        save_result('Step 04 - Guest Picker', page.url, False,
                    'No stepper controls visible')
        raise AssertionError("No stepper increase buttons found")

    # Select 2-5 guests randomly
    total_to_add = random.randint(2, 5)
    added_counts = {'adults': 0, 'children': 0, 'infants': 0, 'pets': 0}
    remaining = total_to_add

    # Always add at least 1 adult
    if 'adults' in available_keys and remaining > 0:
        if _click_stepper_increase(page, 'adults'):
            added_counts['adults'] += 1
            remaining -= 1
            time.sleep(0.35)

    # Distribute remaining randomly
    pool = list(available_keys)
    guard = 0
    while remaining > 0 and pool and guard < 20:
        guard += 1
        key = random.choice(pool)
        if _click_stepper_increase(page, key):
            added_counts[key] += 1
            remaining -= 1
            time.sleep(0.3)
        else:
            pool = [k for k in pool if k != key]

    # Read actual stepper values
    stepper_values = _read_stepper_values(page)
    if any(v > 0 for v in stepper_values.values()):
        added_counts = stepper_values

    total_added = sum(added_counts.values())
    search_guest_count = added_counts['adults'] + added_counts['children']

    print(
        f"  adults={added_counts['adults']} children={added_counts['children']} "
        f"infants={added_counts['infants']} pets={added_counts['pets']}"
    )
    print(f"  Total added: {total_added} | Search guest count: {search_guest_count}")

    set_state('guest_adults', str(added_counts['adults']))
    set_state('guest_children', str(added_counts['children']))
    set_state('guest_infants', str(added_counts['infants']))
    set_state('guest_pets', str(added_counts['pets']))
    set_state('guest_total', str(total_added))

    # Close popup
    try:
        page.keyboard.press('Escape')
        time.sleep(0.5)
    except Exception:
        pass

    # Verify guest display
    guest_display = _get_guest_display(page)
    print(f"  Guest field displays: '{guest_display}'")

    # Click Search
    search_clicked = _click_search(page)
    time.sleep(5)

    comment = (
        f"Country: {country} | Check-in: {checkin} | Check-out: {checkout} | "
        f"adults={added_counts['adults']} children={added_counts['children']} "
        f"infants={added_counts['infants']} pets={added_counts['pets']} | "
        f"Total: {total_added} | Display: '{guest_display}' | Search clicked: {search_clicked}"
    )
    passed = popup_visible and total_added >= 2 and search_clicked

    save_result('Step 04 - Guest Picker', page.url, passed, comment)
    print(f"[Step 04] Done — guests: {total_added} | search clicked: {search_clicked}")
    return added_counts