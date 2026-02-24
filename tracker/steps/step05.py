import re
import time
from urllib.parse import parse_qs, urlparse
from tracker.services import save_result, get_state, set_state


LISTING_CARD_SELECTORS = [
    '[data-testid="listing-card-wrapper"]',
    '[data-testid="card-container"]',
    'article',
]


def _wait_for_results_page(page, timeout=15) -> bool:
    """Poll until URL contains /s/ indicating search results page."""
    for _ in range(timeout):
        if '/s/' in page.url:
            return True
        time.sleep(1)
    return False


def _extract_first_int(text: str):
    match = re.search(r'\d+', text or '')
    if not match:
        return None
    try:
        return int(match.group(0))
    except Exception:
        return None


def _extract_day_token(date_text: str) -> str:
    text = date_text or ''
    month_pattern = (
        r'january|february|march|april|may|june|july|august|'
        r'september|october|november|december|jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec'
    )
    month_first = re.search(
        rf'\b(?:{month_pattern})\.?\s+([0-3]?\d)\b', text, re.IGNORECASE
    )
    if month_first:
        return month_first.group(1).lstrip('0') or '0'
    fallback = re.search(r'\b([0-3]?\d)\b', text)
    if fallback:
        return fallback.group(1).lstrip('0') or '0'
    return ''


def _extract_day_from_iso(date_text: str) -> str:
    match = re.search(r'\b\d{4}-\d{2}-(\d{2})\b', date_text or '')
    if not match:
        return ''
    return match.group(1).lstrip('0') or '0'


def _scrape_listings(page) -> list:
    """Scrape listing cards from results page."""
    listing_elements = []
    used_selector = ''

    for sel in LISTING_CARD_SELECTORS:
        elements = page.query_selector_all(sel)
        if elements:
            listing_elements = elements
            used_selector = sel
            print(f"  Listing cards found via: {sel}")
            break

    listings = []
    for el in listing_elements[:20]:
        listing = {}

        # Title
        for title_sel in [
            '[data-testid="listing-card-title"]',
            'div[role="heading"]',
            'span[id*="title"]',
        ]:
            try:
                t = el.query_selector(title_sel)
                if t:
                    text = t.inner_text().strip()
                    if text:
                        listing['title'] = text
                        break
            except Exception:
                pass

        # Price
        for price_sel in [
            'span[data-testid*="price"]',
            'span._tyxjp1',
            '._1y74zjx',
        ]:
            try:
                p = el.query_selector(price_sel)
                if p:
                    text = p.inner_text().strip()
                    if text:
                        listing['price'] = text
                        break
            except Exception:
                pass

        # Image URL
        try:
            img = el.query_selector('img')
            if img:
                listing['image_url'] = img.get_attribute('src') or ''
        except Exception:
            pass

        # Detail URL
        try:
            a = el.query_selector('a')
            if a:
                href = a.get_attribute('href') or ''
                listing['detail_url'] = (
                    f'https://www.airbnb.com{href}' if href.startswith('/') else href
                )
        except Exception:
            pass

        if listing:
            listings.append(listing)

    return listings


def run(page):
    """Step 05: Verify search results page, validate URL params, scrape listings."""

    time.sleep(3)

    # Restore state
    country = get_state('country')
    checkin = get_state('checkin')
    checkout = get_state('checkout')
    guest_adults = get_state('guest_adults')
    guest_children = get_state('guest_children')
    guest_infants = get_state('guest_infants')
    guest_pets = get_state('guest_pets')
    guest_total = get_state('guest_total')

    print(f"[Step 05] State — country: {country} | checkin: {checkin} | checkout: {checkout}")
    print(f"[Step 05] Guests — adults: {guest_adults} | children: {guest_children} | "
          f"infants: {guest_infants} | pets: {guest_pets} | total: {guest_total}")

    # Wait for results page
    on_results = _wait_for_results_page(page)
    current_url = page.url
    print(f"[Step 05] URL: {current_url[:120]}")

    results_loaded = '/s/' in current_url

    # Parse URL query params
    parsed_url = urlparse(current_url)
    query = parse_qs(parsed_url.query)

    checkin_param = (query.get('checkin') or query.get('check_in') or [''])[0]
    checkout_param = (query.get('checkout') or query.get('check_out') or [''])[0]
    adults_param = (query.get('adults') or ['0'])[0]
    children_param = (query.get('children') or ['0'])[0]
    infants_param = (query.get('infants') or ['0'])[0]
    pets_param = (query.get('pets') or ['0'])[0]

    url_has_checkin = bool(checkin_param)
    url_has_checkout = bool(checkout_param)
    adults_count = _extract_first_int(adults_param) or 0
    children_count = _extract_first_int(children_param) or 0
    infants_count = _extract_first_int(infants_param) or 0
    pets_count = _extract_first_int(pets_param) or 0
    url_guest_total = adults_count + children_count + infants_count + pets_count
    url_has_guests = url_guest_total > 0

    print(f"[Step 05] URL params — checkin: {checkin_param} | checkout: {checkout_param} | "
          f"adults: {adults_count} | children: {children_count} | "
          f"infants: {infants_count} | pets: {pets_count}")

    # Validate dates match
    selected_checkin_day = _extract_day_token(checkin)
    selected_checkout_day = _extract_day_token(checkout)
    url_checkin_day = _extract_day_from_iso(checkin_param)
    url_checkout_day = _extract_day_from_iso(checkout_param)

    url_dates_match = bool(
        selected_checkin_day and selected_checkout_day and
        url_checkin_day and url_checkout_day and
        selected_checkin_day == url_checkin_day and
        selected_checkout_day == url_checkout_day
    )

    # Validate guests match
    expected_guest_total = int(guest_total or 0)
    url_guests_match = (
        expected_guest_total > 0 and url_guest_total == expected_guest_total
    )

    context_matches = all([
        url_has_checkin,
        url_has_checkout,
        url_dates_match,
        url_has_guests,
        url_guests_match,
    ])

    print(f"[Step 05] Dates match: {url_dates_match} | Guests match: {url_guests_match} | "
          f"Context OK: {context_matches}")

    if context_matches:
        print(f"  Selected location, checkin, checkout and guest count appear correctly in URL")
        print(f"  location='{country}' checkin='{checkin}' checkout='{checkout}' "
              f"guests={expected_guest_total}")

    # Scrape listings
    listings = _scrape_listings(page)
    print(f"[Step 05] Scraped {len(listings)} listings")

    # Save each listing as individual Result record
    for listing in listings:
        title = listing.get('title', 'N/A')
        price = listing.get('price', 'N/A')
        image_url = listing.get('image_url', '')
        detail_url = listing.get('detail_url', current_url)
        save_result(
            'Step 05 - Listing Item',
            detail_url,
            True,
            f'Country: {country} | Title: {title} | Price: {price} | Image: {image_url}',
            ''
        )
        print(f"  Listing: {title} | {price}")

    # Save state for step06
    set_state('listings_count', str(len(listings)))
    set_state('results_url', current_url)

    # Store listing detail URLs for step06 to pick from
    detail_urls = [l.get('detail_url', '') for l in listings if l.get('detail_url')]
    set_state('listing_detail_urls', '|||'.join(detail_urls))

    passed = all([
        on_results,
        results_loaded,
        context_matches,
        len(listings) > 0,
    ])

    comment = (
        f"Results loaded: {results_loaded} | "
        f"Context matches: {context_matches} | "
        f"Country: {country} | "
        f"Checkin: {checkin} ({checkin_param}) | "
        f"Checkout: {checkout} ({checkout_param}) | "
        f"Dates match: {url_dates_match} | "
        f"URL guests: {url_guest_total} | Expected: {expected_guest_total} | "
        f"Guests match: {url_guests_match} | "
        f"Listings scraped: {len(listings)}"
    )

    save_result('Step 05 - Results Page', current_url, passed, comment, '')
    print(f"[Step 05] Done — passed: {passed} | listings: {len(listings)}")
    return listings