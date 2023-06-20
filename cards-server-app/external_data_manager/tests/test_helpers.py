from config.helpers import BaseTestCase
from external_data_manager.models import MtgCard
from external_data_manager.helpers import scryfall_search
from unittest.mock import patch, call, MagicMock
from munch import DefaultMunch
from datetime import timedelta

undefined = object()
response_419_munch = DefaultMunch.fromDict(
    {
        "status_code": 419,
    },
    undefined,
)
response_200_munch = DefaultMunch.fromDict(
    {
        "status_code": 200,
    },
    undefined,
)
response_419_munch.json = MagicMock(return_value="419 error")


class TestScryfallPull(BaseTestCase):
    def setUp(self):
        super().setUp()
        response_200_munch.json = MagicMock()

    @patch("requests.get", MagicMock(return_value=response_419_munch))
    def test_scryfall_throws_419_it_returns_none(self):
        self.assertEquals(None, scryfall_search("419 going to occur"))

    @patch("external_data_manager.helpers.get_ckd_price_and_img")
    @patch("requests.get", MagicMock(return_value=response_200_munch))
    def test_scryfall_search_saves_first_card(self, mock_get_ckd_price_and_img):
        expected_price_ckd = "$20.00"
        expected_image_url_ckd = "newckdurl"
        mock_get_ckd_price_and_img.return_value = (
            expected_price_ckd,
            expected_image_url_ckd,
        )
        current_cards = MtgCard.objects.all().count()
        expected_image_uri = "https://image-uri.png"
        expected_price = "$45.99"
        expected_name = "Test!"
        expected_type_line = "Some type"
        expected_mana_cost = "2U"

        expected_data = {
            "object": "list",
            "total_cards": 2,
            "data": [
                {
                    "image_uris": {
                        "normal": expected_image_uri,
                    },
                    "name": expected_name,
                    "mana_cost": expected_mana_cost,
                    "type_line": expected_type_line,
                    "prices": {"usd": expected_price},
                },
                {
                    "image_uris": {
                        "normal": expected_image_uri + "no",
                    },
                    "name": expected_name + "no",
                    "mana_cost": expected_mana_cost + "no",
                    "type_line": expected_type_line + "no",
                    "prices": {"usd": "$1," + expected_price},
                },
            ],
        }
        response_200_munch.json.return_value = expected_data

        given_search = "test"
        card = scryfall_search(given_search)

        self.assertEquals(expected_name, card.name)
        self.assertEquals(expected_image_uri, card.image_url)
        self.assertNotEquals(None, card.created)
        self.assertNotEquals(None, card.last_updated)
        self.assertEquals(expected_price, card.price)
        self.assertEquals(expected_type_line, card.type_line)
        self.assertEquals(expected_mana_cost, card.mana_cost)
        self.assertEquals(expected_data["data"][0], card.latest_card_data)
        self.assertEquals(given_search, card.search_text)

        self.assertEquals(current_cards + 1, MtgCard.objects.all().count())

    def test_search_text_on_card_gets_lowercased_and_stripped_of_spaces(self):
        card = MtgCard.objects.create(name="test_cache", search_text="   DEF     cow ")
        card.save()
        card.refresh_from_db()

        self.assertEquals("def cow", card.search_text)

    @patch("requests.get")
    def test_scryfall_item_is_cached_less_than_24_hours_it_uses_cache(
        self, mock_request
    ):
        existing_card = MtgCard.objects.create(name="test_cache", search_text="abc")

        returned_card = scryfall_search("abc")

        assert not mock_request.called
        self.assertEquals(existing_card, returned_card)

    @patch("requests.get")
    def test_scryfall_item_is_cached_is_case_and_space_agnostic(self, mock_request):
        existing_card = MtgCard.objects.create(name="test_cache", search_text="abc dog")

        returned_card = scryfall_search("ABC dog")

        assert not mock_request.called
        self.assertEquals(existing_card, returned_card)

        returned_card = scryfall_search(" Abc  dog ")

        assert not mock_request.called
        self.assertEquals(existing_card, returned_card)

    @patch("external_data_manager.helpers.get_ckd_price_and_img")
    @patch("requests.get")
    def test_scryfall_item_is_cached_over_24_hours_it_replaces_cache(
        self, mock_request, mock_get_ckd_price_and_img
    ):
        expected_price_ckd = "$20.00"
        expected_image_url_ckd = "newckdurl"
        mock_get_ckd_price_and_img.return_value = (
            expected_price_ckd,
            expected_image_url_ckd,
        )
        mock_request.return_value = response_200_munch
        expected_name = "new name"
        expected_image_uri = "https://image-uri.png"
        expected_price = "$45.99"
        expected_name = "Test!"
        expected_type_line = "Some type"
        expected_mana_cost = "2U"

        expected_data = {
            "object": "list",
            "total_cards": 2,
            "data": [
                {
                    "image_uris": {
                        "normal": expected_image_uri,
                    },
                    "name": expected_name,
                    "mana_cost": expected_mana_cost,
                    "type_line": expected_type_line,
                    "prices": {"usd": expected_price},
                },
                {},
            ],
        }
        response_200_munch.json.return_value = expected_data

        existing_card = MtgCard.objects.create(
            name="test_cache",
            search_text="abc",
            price_ckd="$30",
            image_url_ckd="oldckdimage",
        )
        initial_card_count = MtgCard.objects.all().count()
        original_created = existing_card.created
        right_before_cache_expiry = existing_card.last_updated - timedelta(
            hours=23, minutes=59
        )
        MtgCard.objects.filter(search_text="abc").update(
            last_updated=right_before_cache_expiry
        )

        returned_card = scryfall_search("abc")

        assert not mock_request.called
        assert not mock_get_ckd_price_and_img.called
        self.assertEquals(right_before_cache_expiry, returned_card.last_updated)

        right_at_cache_expiry = existing_card.last_updated - timedelta(
            hours=24, seconds=1
        )
        MtgCard.objects.filter(search_text="abc").update(
            last_updated=right_at_cache_expiry
        )
        second_returned_card = scryfall_search("abc")
        assert mock_request.called
        self.assertNotEquals(
            right_before_cache_expiry, second_returned_card.last_updated
        )
        self.assertEquals(original_created, second_returned_card.created)
        self.assertEquals(initial_card_count, MtgCard.objects.all().count())
        self.assertEquals(expected_name, second_returned_card.name)
        self.assertEquals(expected_image_uri, second_returned_card.image_url)
        self.assertNotEquals(None, second_returned_card.created)
        self.assertNotEquals(None, second_returned_card.last_updated)
        self.assertEquals(expected_price, second_returned_card.price)
        self.assertEquals(expected_type_line, second_returned_card.type_line)
        self.assertEquals(expected_mana_cost, second_returned_card.mana_cost)
        self.assertEquals(
            expected_data["data"][0], second_returned_card.latest_card_data
        )
        self.assertEquals(expected_price_ckd, second_returned_card.price_ckd)
        self.assertEquals(expected_image_url_ckd, second_returned_card.image_url_ckd)

    @patch("external_data_manager.helpers.get_ckd_price_and_img")
    @patch("requests.get", MagicMock(return_value=response_200_munch))
    def test_scryfall_get_card_image_from_front_face_or_first_image(
        self, mock_get_ckd_price_and_img
    ):
        mock_get_ckd_price_and_img.return_value = ("", "")
        current_cards = MtgCard.objects.all().count()
        expected_image_uri = "https://image-uri.png"
        expected_price = "$45.99"
        expected_name = "Test!"
        expected_type_line = "Some type"
        expected_mana_cost = "2U"

        expected_data = {
            "object": "list",
            "total_cards": 2,
            "data": [
                {
                    "card_faces": [
                        {
                            "image_uris": {
                                "normal": expected_image_uri,
                            },
                        }
                    ],
                    "mana_cost": expected_mana_cost,
                    "name": expected_name,
                    "type_line": expected_type_line,
                    "prices": {"usd": expected_price},
                },
            ],
        }
        response_200_munch.json.return_value = expected_data

        given_search = "test"
        card = scryfall_search(given_search)

        self.assertEquals(expected_name, card.name)
        self.assertEquals(expected_image_uri, card.image_url)
        self.assertNotEquals(None, card.created)
        self.assertNotEquals(None, card.last_updated)
        self.assertEquals(expected_price, card.price)
        self.assertEquals(expected_type_line, card.type_line)
        self.assertEquals(expected_mana_cost, card.mana_cost)
        self.assertEquals(expected_data["data"][0], card.latest_card_data)
        self.assertEquals(given_search, card.search_text)

        self.assertEquals(current_cards + 1, MtgCard.objects.all().count())

    @patch("external_data_manager.helpers.get_ckd_price_and_img")
    @patch("requests.get", MagicMock(return_value=response_200_munch))
    def test_scryfall_get_manacost_from_front_face_or_main(
        self, mock_get_ckd_price_and_img
    ):
        mock_get_ckd_price_and_img.return_value = ("", "")
        current_cards = MtgCard.objects.all().count()
        expected_image_uri = "https://image-uri.png"
        expected_price = "$45.99"
        expected_name = "Test!"
        expected_type_line = "Some type"
        expected_mana_cost = "2U"

        expected_data = {
            "object": "list",
            "total_cards": 2,
            "data": [
                {
                    "card_faces": [
                        {
                            "mana_cost": expected_mana_cost,
                        }
                    ],
                    "image_uris": {
                        "normal": expected_image_uri,
                    },
                    "name": expected_name,
                    "type_line": expected_type_line,
                    "prices": {"usd": expected_price},
                },
            ],
        }
        response_200_munch.json.return_value = expected_data

        given_search = "test"
        card = scryfall_search(given_search)

        self.assertEquals(expected_name, card.name)
        self.assertEquals(expected_image_uri, card.image_url)
        self.assertNotEquals(None, card.created)
        self.assertNotEquals(None, card.last_updated)
        self.assertEquals(expected_price, card.price)
        self.assertEquals(expected_type_line, card.type_line)
        self.assertEquals(expected_mana_cost, card.mana_cost)
        self.assertEquals(expected_data["data"][0], card.latest_card_data)
        self.assertEquals(given_search, card.search_text)

        self.assertEquals(current_cards + 1, MtgCard.objects.all().count())
