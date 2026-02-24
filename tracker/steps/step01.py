import os
import random
from tracker.services import save_result, set_state

AIRBNB_URL = os.getenv('AIRBNB_URL', 'https://www.airbnb.com/')

TOP_20_COUNTRIES = [
    'United States', 'China', 'India', 'Brazil', 'Russia',
    'Indonesia', 'Pakistan', 'Nigeria', 'Bangladesh', 'Ethiopia',
    'Mexico', 'Japan', 'Philippines', 'Egypt',
    'Vietnam', 'Iran', 'Turkey', 'Germany', 'Thailand', 'France',
]


def close_popups(page):
    page.evaluate("""() => {
        document.querySelectorAll('[data-testid="modal-container"]').forEach(el => el.remove());
        document.querySelectorAll('div[role="dialog"]').forEach(el => el.remove());
    }""")
    page.wait_for_timeout(500)


def run(page):
    page.goto(AIRBNB_URL, wait_until='domcontentloaded')
    page.wait_for_timeout(5000)
    page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")
    page.context.clear_cookies()
    close_popups(page)

    assert 'airbnb' in page.url.lower(), "Homepage did not load"
    save_result('Step 01 - Homepage Load', page.url, True, 'Homepage loaded', '')
    print("[Step 01] Homepage loaded")

    countries = TOP_20_COUNTRIES.copy()
    random.shuffle(countries)
    country = None
    chosen_text = None
    suggestion_data = []

    for candidate in countries:
        print(f"  Trying: {candidate}")

        query_field = page.get_by_test_id("structured-search-input-field-query")
        query_field.wait_for(state='visible', timeout=10000)
        close_popups(page)
        query_field.click()
        page.wait_for_timeout(500)
        query_field.fill("")
        page.wait_for_timeout(300)

        for char in candidate:
            page.keyboard.type(char, delay=150)
        page.wait_for_timeout(3000)

        suggestion_locator = page.locator('div[id^="bigsearch-query-location-suggestion-"]')
        try:
            suggestion_locator.first.wait_for(state='visible', timeout=5000)
        except Exception:
            print(f"  No suggestions for {candidate}")
            continue

        suggestions = page.evaluate(
            "() => {"
            "  var items = document.querySelectorAll('div[id^=\"bigsearch-query-location-suggestion-\"]');"
            "  return Array.from(items).map(function(el, idx) {"
            "    return {"
            "      id: el.getAttribute('id'),"
            "      text: (el.innerText || '').trim(),"
            "      hasIcon: el.querySelector('svg') !== null,"
            "      index: idx"
            "    };"
            "  }).filter(function(s) { return s.text && s.id; });"
            "}"
        )

        if not suggestions:
            continue

        print(f"  Found {len(suggestions)} suggestions")

        # Find exact match
        preferred_index = None
        for s in suggestions:
            if s['text'].strip().lower() == candidate.lower():
                preferred_index = s['index']
                print(f"  Exact match at index {preferred_index}: '{s['text']}'")
                break
        if preferred_index is None:
            for s in suggestions:
                if s['text'].strip().lower().startswith(candidate.lower()):
                    preferred_index = s['index']
                    print(f"  Starts-with at index {preferred_index}: '{s['text']}'")
                    break
        if preferred_index is None:
            preferred_index = 0

        # Click option
        try:
            option = page.get_by_test_id(f"option-{preferred_index}")
            option.wait_for(state='visible', timeout=5000)
            option.click()
            page.wait_for_timeout(3000)
        except Exception as e:
            print(f"  option-{preferred_index} failed: {e}")
            for _ in range(preferred_index + 1):
                page.keyboard.press('ArrowDown')
                page.wait_for_timeout(200)
            page.keyboard.press('Enter')
            page.wait_for_timeout(3000)

        try:
            retained = query_field.input_value()
        except Exception:
            retained = ''
        print(f"  Location retained: '{retained}'")

        if retained:
            suggestion_data = suggestions
            chosen_text = suggestions[preferred_index]['text']
            country = candidate
            set_state('country', country)
            set_state('chosen_suggestion', chosen_text)
            break

    assert country, "Could not select any country"

    save_result('Step 01 - Search Input', page.url, True, f'Country: {country}', '')
    print(f"[Step 01] Done — typed: {country}")

    for item in suggestion_data:
        save_result('Step 02 - Auto-suggestion Item', page.url, True,
                    f"Suggestion: {item['text']} | Map icon: {item['hasIcon']}", '')
        print(f"  Suggestion: {item['text']} | map icon: {item['hasIcon']}")

    save_result('Step 02 - Auto-suggestion List', page.url, True,
                f'Country: {country} | Suggestions: ' + ', '.join([s['text'] for s in suggestion_data]), '')
    save_result('Step 02 - Suggestion Selected', page.url, True,
                f'Selected: {chosen_text}', '')
    print(f"[Step 02] Done — selected: {chosen_text}")