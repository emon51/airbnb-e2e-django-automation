import random
from tracker.models import ListingItem
from tracker.services import save_result, take_screenshot


def run(page):
    """Step 06: Click a random listing and verify its details page."""

    # Get all listing cards on results page
    listing_cards = page.locator('[data-testid="listing-card-wrapper"]').all()
    assert len(listing_cards) > 0, "No listings available to select"

    # Randomly pick one listing
    chosen = random.choice(listing_cards)

    # Get detail URL before clicking (opening in same tab)
    link = chosen.locator('a').first
    link.click()
    page.wait_for_load_state('domcontentloaded')
    page.wait_for_timeout(3000)

    current_url = page.url
    assert 'airbnb.com/rooms' in current_url or 'airbnb.com/h/' in current_url, \
        f"Details page did not open correctly: {current_url}"

    take_screenshot(page, 'step06_details_page')

    # Capture title
    try:
        title = page.locator('h1').first.inner_text().strip()
    except Exception:
        title = 'N/A'

    # Capture subtitle
    try:
        subtitle = page.locator('h2').first.inner_text().strip()
    except Exception:
        subtitle = 'N/A'

    # Collect all image URLs from the gallery
    images = page.locator('img[data-original-uri], img[src*="muscache"]').all()
    image_urls = []
    for img in images:
        src = img.get_attribute('src') or ''
        if src and src not in image_urls:
            image_urls.append(src)

    # Update the matching ListingItem with detail info if exists
    ListingItem.objects.filter(detail_url=current_url).update(
        title=title,
        image_url=image_urls[0] if image_urls else ''
    )

    save_result(
        'Listing Details Page',
        current_url,
        True,
        f'Title: {title} | Subtitle: {subtitle} | Images found: {len(image_urls)}'
    )

    print(f"[Step 06] Done — Title: {title}")
    print(f"  Subtitle: {subtitle}")
    print(f"  Images collected: {len(image_urls)}")