from external_data_manager.models import (
    MtgCard,
    MtgStore,
    AdditionalStep,
    MtgStorePrice,
)
from playwright.sync_api import sync_playwright
from celery import shared_task
import re
from decimal import Decimal, getcontext


def get_prices_for_card(card: MtgCard):
    stores = []
    for x in MtgStore.objects.all():
        steps = []
        for y in x.additionalstep_set.order_by("order"):
            steps.append(y)

        stores.append((x, steps, []))
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        for x in stores:
            print(f"looking up {x[0].name}")
            url_to_open = x[0].search_url.replace("{card}", card.name)
            page.goto(url_to_open)
            page.screenshot(path=x[0].name + "list.png")
            if x[1]:
                for y in x[1]:
                    if y.action == AdditionalStep.Action.CLICK:
                        page.locator(y.item_locator).click()
                    elif y.action == AdditionalStep.Action.FILL:
                        page.locator(y.item_locator).fill(card.name)
            for pl in page.locator(x[0].item_locator).all():
                card_name = pl.locator(x[0].item_name_locator).inner_text()
                price = pl.locator(x[0].item_price_locator).inner_text()
                price_numeric = re.sub(r"[^0-9.]", "", price)
                x[2].append(card_name, price_numeric)

        browser.close()
    return stores


def _name_matches(to_match, value):
    # Remove text after " - "
    value = re.sub(r"\s-\s.*", "", value)

    # Remove text inside parentheses
    value = re.sub(r"\([^()]*\)", "", value)

    return value.strip() == to_match.strip()


@shared_task
def update_prices_for_card(card_id: int):
    card = MtgCard.objects.get(pk=card_id)
    prices = get_prices_for_card(card)
    getcontext().prec = 2

    for store in prices:
        matching_data = [item for item in store[2] if _name_matches(card.name, item[0])]
        lowest_price = min(matching_data, key=lambda x: Decimal(x[1]))
        MtgStorePrice.objects.update_or_create(
            store=store[0], card=card, defaults={"price": Decimal(lowest_price[1])}
        )
