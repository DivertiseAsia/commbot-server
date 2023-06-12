import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class MtgCard(models.Model):
    ##TODO: create task server to grab updates from time to time.
    ##TODO: see if can grab prices from ckd; links to sabai/fizzy
    name = models.CharField(max_length=255)
    created = models.DateTimeField(_("First Created"), auto_now_add=True)
    last_updated = models.DateTimeField(_("Last Updated"), auto_now=True)
    latest_card_data = models.JSONField(default=dict, blank=True)

    image_url = models.CharField(max_length=255)
    price = models.CharField(max_length=20, blank=True, null=True)
    type_line = models.CharField(max_length=255)
    mana_cost = models.CharField(max_length=64)

    search_text = models.CharField(max_length=255, db_index=True, unique=True)
    external_id = models.CharField(
        _("External ID (from Provider)"), max_length=255, blank=True, db_index=True
    )

    def save(self, *args, **kwargs):
        self.search_text = " ".join(self.search_text.split()).lower()
        super(MtgCard, self).save(*args, **kwargs)
