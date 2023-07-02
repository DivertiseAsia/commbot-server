from config.helpers import BaseTestCase
from external_data_manager.models import MtgCard, MtgStore, MtgStorePrice
from unittest.mock import patch, MagicMock
from munch import DefaultMunch
from external_data_manager.tasks import update_prices_for_card
from decimal import Decimal
import time

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


class TestUpdatePrices(BaseTestCase):
    def setUp(self):
        super().setUp()
        self.store_a = MtgStore.objects.create(name="store_a")
        self.store_b = MtgStore.objects.create(name="store_b")

        self.card_name = "Test Card"
        self.test_card = MtgCard.objects.create(name=self.card_name)

        self.initial_price_objects = MtgStorePrice.objects.all().count()

    @patch("external_data_manager.tasks.get_prices_for_card")
    def test_update_prices_sorts(self, mock_get_prices):
        mock_prices = []
        mock_prices.append(
            (
                self.store_a,
                [],
                [(self.card_name, "1.23"), (self.card_name, "0.25")],
            )
        )
        mock_prices.append(
            (self.store_b, [], [(self.card_name, "15"), (self.card_name, "1.25")])
        )
        mock_get_prices.return_value = list(mock_prices)

        update_prices_for_card(self.test_card.pk)

        self.assertEquals(
            MtgStorePrice.objects.all().count(), self.initial_price_objects + 2
        )
        self.assertEquals(
            Decimal("0.25"),
            MtgStorePrice.objects.get(card=self.test_card, store=self.store_a).price,
        )
        self.assertEquals(
            Decimal("1.25"),
            MtgStorePrice.objects.get(card=self.test_card, store=self.store_b).price,
        )

    @patch("external_data_manager.tasks.get_prices_for_card")
    def test_update_prices_running_twice_only_updates_not_creates_2x(
        self, mock_get_prices
    ):
        mock_prices = []
        mock_prices.append(
            (
                self.store_a,
                [],
                [(self.card_name, "11.23")],
            )
        )
        mock_get_prices.return_value = list(mock_prices)

        update_prices_for_card(self.test_card.pk)

        self.assertEquals(
            MtgStorePrice.objects.all().count(), self.initial_price_objects + 1
        )

        update_prices_for_card(self.test_card.pk)

        store_price_object = MtgStorePrice.objects.get(
            card=self.test_card, store=self.store_a
        )
        initial_update = store_price_object.last_updated

        self.assertEquals(
            Decimal("11.23"),
            store_price_object.price,
        )

        time.sleep(0.1)
        mock_prices = []
        mock_prices.append(
            (
                self.store_a,
                [],
                [(self.card_name, "1.29")],
            )
        )
        mock_get_prices.return_value = list(mock_prices)

        update_prices_for_card(self.test_card.pk)
        store_price_object.refresh_from_db()
        self.assertNotEquals(store_price_object.last_updated, initial_update)
        self.assertEquals(store_price_object.price, Decimal("1.29"))
        self.assertEquals(
            MtgStorePrice.objects.all().count(), self.initial_price_objects + 1
        )

    @patch("external_data_manager.tasks.get_prices_for_card")
    def test_update_prices_only_if_matching_name_ignoring_otherstuff(
        self, mock_get_prices
    ):
        mock_prices = []
        mock_prices.append(
            (
                self.store_a,
                [],
                [
                    (self.card_name + " - foil", "1.00"),
                    ("TEST" + self.card_name, "0.01"),
                ],
            )
        )
        mock_prices.append(
            (
                self.store_b,
                [],
                [
                    ("fail " + self.card_name, "1.25"),
                    (self.card_name + " (test) [extra]", "10.00"),
                ],
            )
        )
        mock_get_prices.return_value = list(mock_prices)

        update_prices_for_card(self.test_card.pk)

        self.assertEquals(
            MtgStorePrice.objects.all().count(), self.initial_price_objects + 2
        )
        self.assertEquals(
            Decimal("1.00"),
            MtgStorePrice.objects.get(card=self.test_card, store=self.store_a).price,
        )
        self.assertEquals(
            Decimal("10.00"),
            MtgStorePrice.objects.get(card=self.test_card, store=self.store_b).price,
        )

    @patch("external_data_manager.tasks.get_prices_for_card")
    def test_update_prices_no_results_doesnt_explode(self, mock_get_prices):
        mock_prices = []
        mock_prices.append(
            (
                self.store_a,
                [],
                [],
            )
        )
        mock_prices.append(
            (
                self.store_b,
                [],
                [
                    ("fail " + self.card_name, "1.25"),
                    (self.card_name + " (test)", "10.00"),
                ],
            )
        )
        mock_get_prices.return_value = list(mock_prices)

        update_prices_for_card(self.test_card.pk)

        self.assertEquals(
            MtgStorePrice.objects.all().count(), self.initial_price_objects + 1
        )
