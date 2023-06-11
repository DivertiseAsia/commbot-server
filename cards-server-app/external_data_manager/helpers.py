import requests


def scryfall_first_card(cards):
    return cards[0]


def scryfall_card_image(card):
    return card["image_uris"]["normal"]


def scryfall_card_price(card):
    return card["prices"]["usd"]


def scryfall_search(query):
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
            return data["data"]
    else:
        print("scryfall had an issue code:", response.status_code)
        print("error:", response.json())
    return None
