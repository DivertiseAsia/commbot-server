
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from user_manager.models import Profile

User = get_user_model()


class UserBookStorage(models.Model):
    owner = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    # books =