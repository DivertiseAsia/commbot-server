from comm_manager.models import ChatUser
from django.db import models


class Event(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=255)
    date = models.DateField()
    time = models.TimeField(null=True, blank=True)
    venue_name = models.CharField(max_length=255)
    cost = models.CharField(max_length=255)
    min_participants = models.IntegerField(default=0)
    max_participants = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} on {self.date} @ {self.venue_name}"


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=True, blank=True)

    chat_user = models.ForeignKey(
        ChatUser, on_delete=models.SET_NULL, null=True, blank=True
    )

    @property
    def display_name(self):
        if self.chat_user:
            return self.chat_user.display_name
        return self.name

    def __str__(self):
        return self.display_name
