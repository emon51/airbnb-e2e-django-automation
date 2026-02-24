import random
import time
from tracker.services import save_result, get_state


def run(page):
    """Step 06: Click a random listing and verify its details page."""

    time.sleep(1)

    country = get_state('country')
    checkin = get_state('checkin')
    checkout = get_state('checkout')
    print(f"[Step 06] State — country: {country} | checkin: {checkin} | checkout: {checkout}")

    # Collect all listing card hrefs first
    detail_urls = page.evaluate("""() => {
        const cards = Array.from(document.querySelectorAll(
            '[data-testid="card-container"], [data-testid="listing-card-wrapper"], article'
        ));
        const urls = [];
        for (const card of cards) {
            const a = card.querySelector('a[href*="/rooms/"], a[href*="/h/"]');
            if (a) {
                const href = a.getAttribute('href');
                if (href) {
                    const url = href.startsWith('http') ? href : 'https://www.airbnb.com' + href;
                    if (!urls.includes(url)) urls.push(url);
                }
            }
        }
        return urls;
    }""")

    print(f"[Step 06] Found {len(detail_urls)} detail URLs")

    assert len(detail_urls) > 0, "No listing detail URLs found on results page"

    # Pick a random listing URL and navigate directly
    chosen_url = random.choice(detail_urls)
    print(f"[Step 06] Navigating to: {chosen_url[:80]}")

    page.goto(chosen_url, wait_until='domcontentloaded')
    time.sleep(3)

    current_url = page.url
    is_detail_page = '/rooms/' in current_url or '/h/' in current_url
    assert is_detail_page, f"Details page did not open: {current_url}"

    print(f"[Step 06] Detail page confirmed: {current_url[:100]}")

    # Scrape title
    try:
        title = page.locator('h1').first.inner_text().strip()
    except Exception:
        title = 'N/A'

    # Scrape subtitle
    try:
        subtitle = page.locator('h2').first.inner_text().strip()
    except Exception:
        subtitle = 'N/A'

    # Scrape rating
    try:
        rating = page.evaluate("""() => {
            const el = document.querySelector(
                '[aria-label*="rating"], [data-testid*="rating"], span[class*="rating"]'
            );
            return el ? el.innerText.trim() : '';
        }""")
    except Exception:
        rating = ''

    # Scrape host name
    try:
        host = page.evaluate("""() => {
            const els = Array.from(document.querySelectorAll('h2, h3'));
            const el = els.find(e => (e.innerText || '').toLowerCase().includes('hosted by'));
            return el ? el.innerText.trim() : '';
        }""")
    except Exception:
        host = ''

    # Scrape amenities
    try:
        amenities = page.evaluate("""() => {
            const items = Array.from(document.querySelectorAll(
                '[data-testid="amenity-row"] span, [data-testid*="amenities"] li, div[class*="amenity"]'
            ));
            return items.slice(0, 10).map(el => el.innerText.trim()).filter(Boolean);
        }""")
    except Exception:
        amenities = []

    # Scrape price on detail page
    try:
        price = page.evaluate("""() => {
            const el = document.querySelector(
                '[data-testid*="price"], span[class*="price"], ._tyxjp1'
            );
            return el ? el.innerText.trim() : '';
        }""")
    except Exception:
        price = ''

    # Scrape all images
    image_urls = []
    try:
        images = page.query_selector_all('img[data-original-uri], img[src*="muscache"]')
        for img in images:
            src = img.get_attribute('src') or ''
            if src and src not in image_urls:
                image_urls.append(src)
    except Exception:
        pass

    print(f"[Step 06] Title: {title}")
    print(f"[Step 06] Subtitle: {subtitle}")
    print(f"[Step 06] Host: {host}")
    print(f"[Step 06] Rating: {rating}")
    print(f"[Step 06] Price: {price}")
    print(f"[Step 06] Amenities: {amenities[:5]}")
    print(f"[Step 06] Images: {len(image_urls)}")

    # Save each image as Result record
    for img_url in image_urls:
        save_result(
            'Step 06 - Listing Image',
            current_url,
            True,
            f'Image URL: {img_url}',
            ''
        )

    # Save amenities
    if amenities:
        save_result(
            'Step 06 - Listing Amenities',
            current_url,
            True,
            f'Amenities: {", ".join(amenities)}',
            ''
        )

    comment = (
        f"Country: {country} | Checkin: {checkin} | Checkout: {checkout} | "
        f"Title: {title} | Subtitle: {subtitle} | Host: {host} | "
        f"Rating: {rating} | Price: {price} | "
        f"Amenities: {len(amenities)} | Images: {len(image_urls)}"
    )

    save_result('Step 06 - Listing Details', current_url, True, comment, '')
    print(f"[Step 06] Done — Title: {title} | Images: {len(image_urls)}")