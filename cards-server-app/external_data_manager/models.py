import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class MtgStore(models.Model):
    name = models.CharField(max_length=100)
    search_url = models.CharField(max_length=255)
    item_locator = models.CharField(max_length=100)
    item_price_locator = models.CharField(max_length=100)
    item_name_locator = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AdditionalStep(models.Model):
    class Action(models.IntegerChoices):
        FILL = 1
        CLICK = 2

    order = models.IntegerField()
    item_locator = models.CharField(max_length=100)
    action = models.IntegerField(choices=Action.choices)
    store = models.ForeignKey(MtgStore, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("order", "store")


class MtgCard(models.Model):
    ##TODO: create task server to grab updates from time to time.
    ##TODO: see if can grab prices from ckd; links to sabai/fizzy
    name = models.CharField(max_length=255)
    created = models.DateTimeField(_("First Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)
    latest_card_data = models.JSONField(default=dict, blank=True)

    image_url = models.CharField(max_length=255)
    image_url_ckd = models.CharField(max_length=255, blank=True, null=True)
    price = models.CharField(max_length=20, blank=True, null=True)
    price_ckd = models.CharField(max_length=20, blank=True, null=True)
    type_line = models.CharField(max_length=255)
    mana_cost = models.CharField(max_length=64)

    search_text = models.CharField(max_length=255, db_index=True, unique=True)
    external_id = models.CharField(
        _("External ID (from Provider)"), max_length=255, blank=True, db_index=True
    )
    prices = models.ManyToManyField(MtgStore, through="MtgStorePrice")

    @staticmethod
    def get_url_ckd_search(card_name):
        return f"https://www.cardkingdom.com/catalog/search?search=header&filter%5Bname%5D=%22{card_name}%22&filter%5Bcategory_id%5D=0&filter%5Btype_mode%5D=any&filter%5Btype%5D%5B0%5D=any&filter%5Bprice_op%5D=&filter%5Bprice%5D=&filter%5Bprice_max%5D=&filter%5Bfoil%5D=1&filter%5Bnonfoil%5D=1&filter%5Bsort%5D=name&filter%5Bsort_dir%5D"

    @property
    def url_ckd_search(self):
        return self.__class__.get_url_ckd_search(self.name)

    def save(self, *args, **kwargs):
        self.search_text = " ".join(self.search_text.split()).lower()
        super(MtgCard, self).save(*args, **kwargs)


class MtgStorePrice(models.Model):
    store = models.ForeignKey(MtgStore, on_delete=models.CASCADE)
    card = models.ForeignKey(MtgCard, on_delete=models.CASCADE)
    price = models.CharField(max_length=20, blank=True, null=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)
