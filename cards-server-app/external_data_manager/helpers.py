import requests
from external_data_manager.models import MtgCard
from datetime import timedelta
from django.utils import timezone
from playwright.sync_api import sync_playwright
import logging

logger = logging.getLogger("external_data_manager__helpers")


def get_ckd_price_and_img(card: str):
    try:
        with sync_playwright() as p:
            browser = p.firefox.launch()
            page = browser.new_page()
            page.goto(MtgCard.get_url_ckd_search(card))

            card = page.locator(".productCardWrapper").filter(has_text=card).nth(0)
            card_price = card.locator(".NM span.stylePrice").inner_text().strip()
            card_image = card.locator("img").get_attribute("src")
            return (card_price, card_image)
    except Exception as e:
        logger.warning("Issue with ckd price and image", e)
        return ("", "")


def scryfall_search(query):
    query = " ".join(query.split()).lower()
    last_24_hours = timezone.now() - timedelta(hours=24)
    existing_card_qs = MtgCard.objects.filter(
        search_text=query, last_updated__gte=last_24_hours
    )
    if existing_card_qs.exists():
        return existing_card_qs.first()
    else:
        print("doing query")
        url = "https://api.scryfall.com/cards/search"
        params = {
            "q": query,
            "unique": "prints",
            "order": "name",
            "dir": "asc",
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            data = response.json()

            if data["object"] == "error":
                print("Scryfall had an error", data)
                return None

            if data["total_cards"] > 0:
                card = data["data"][0]

                card_obj, _ = MtgCard.objects.get_or_create(search_text=query)
                card_obj.name = card["name"]
                if "image_uris" in card:
                    card_obj.image_url = card["image_uris"]["normal"]
                else:
                    card_obj.image_url = card["card_faces"][0]["image_uris"]["normal"]
                card_obj.price = card["prices"]["usd"]
                card_obj.type_line = card["type_line"]
                if "mana_cost" in card:
                    card_obj.mana_cost = card["mana_cost"]
                else:
                    card_obj.mana_cost = card["card_faces"][0]["mana_cost"]
                card_obj.latest_card_data = card
                ckd_price, ckd_image = get_ckd_price_and_img(card["name"])
                card_obj.price_ckd = ckd_price
                card_obj.image_url_ckd = ckd_image
                card_obj.save()
                return card_obj
        else:
            print("scryfall had an issue code:", response.status_code)
            print("error:", response.json())
        return None
