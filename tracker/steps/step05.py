from tracker.models import ListingItem
from tracker.services import save_result, take_screenshot


def run(page):
    """Step 05: Verify search results page and scrape listing data."""

    # Wait for results page to load
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(3000)

    current_url = page.url

    # Verify page loaded successfully
    assert 'airbnb.com' in current_url, "Search results page did not load"
    take_screenshot(page, 'step05_results_page')

    # Confirm dates and guests appear in URL
    url_has_dates = 'check_in' in current_url or 'checkin' in current_url
    url_has_guests = 'adults' in current_url or 'guests' in current_url
    save_result(
        'Search Results URL Validation',
        current_url,
        url_has_dates and url_has_guests,
        f'URL has dates: {url_has_dates} | URL has guests: {url_has_guests}'
    )

    # Scrape listings — title, price, image
    listing_cards = page.locator('[data-testid="listing-card-wrapper"]').all()
    assert len(listing_cards) > 0, "No listings found on results page"

    scraped = []
    for card in listing_cards:
        try:
            title = card.locator('[data-testid="listing-card-title"]').first.inner_text().strip()
        except Exception:
            title = 'N/A'

        try:
            price = card.locator('span._tyxjp1').first.inner_text().strip()
        except Exception:
            price = 'N/A'

        try:
            image_url = card.locator('img').first.get_attribute('src') or ''
        except Exception:
            image_url = ''

        try:
            link = card.locator('a').first.get_attribute('href') or ''
            detail_url = f'https://www.airbnb.com{link}' if link.startswith('/') else link
        except Exception:
            detail_url = ''

        ListingItem.objects.create(
            title=title,
            price=price,
            image_url=image_url,
            detail_url=detail_url,
        )
        scraped.append(title)
        print(f"  Listing: {title} | {price}")

    save_result(
        'Search Results Scraping',
        current_url,
        True,
        f'Scraped {len(scraped)} listings: ' + ', '.join(scraped[:5])
    )

    print(f"[Step 05] Done — scraped {len(scraped)} listings")
    return listing_cards