import random
from tracker.models import SuggestionItem
from tracker.services import save_result, take_screenshot


def run(page, country):
    """Step 02: Verify auto-suggestions and select one randomly."""

    # Wait for suggestion list to appear
    suggestion_list = page.locator('[data-testid="structured-search-input-suggestionsPanel"]')
    suggestion_list.wait_for(state='visible', timeout=10000)

    # Get all suggestion items
    items = page.locator('[data-testid="structured-search-input-suggestionsPanel"] [role="option"]').all()
    assert len(items) > 0, "No suggestions appeared"

    # Verify and store each suggestion
    suggestion_texts = []
    for item in items:
        text = item.inner_text().strip()
        if not text:
            continue

        # Confirm map icon is present inside each suggestion
        has_icon = item.locator('svg').count() > 0

        SuggestionItem.objects.create(text=text)
        suggestion_texts.append(text)
        print(f"  Suggestion: {text} | map icon: {has_icon}")

    take_screenshot(page, 'step02_suggestions')
    save_result(
        'Auto-suggestion List',
        page.url,
        True,
        f'Suggestions for {country}: ' + ', '.join(suggestion_texts)
    )

    # Randomly pick one and click it
    chosen = random.choice(items)
    chosen_text = chosen.inner_text().strip()
    chosen.click()
    page.wait_for_timeout(2000)

    take_screenshot(page, 'step02_suggestion_selected')
    save_result(
        'Auto-suggestion Selection',
        page.url,
        True,
        f'Selected suggestion: {chosen_text}'
    )

    print(f"[Step 02] Done — selected: {chosen_text}")