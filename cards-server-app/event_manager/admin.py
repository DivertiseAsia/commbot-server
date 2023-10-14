from datetime import date

from django.contrib import admin

from .models import Event, Participant


class UpcomingEventFilter(admin.SimpleListFilter):
    title = "upcoming status"
    parameter_name = "upcoming"

    def lookups(self, request, model_admin):
        return (
            ("upcoming", "Upcoming"),
            ("past", "Past"),
        )

    def queryset(self, request, queryset):
        if self.value() == "upcoming":
            return queryset.filter(date__gte=date.today())
        if self.value() == "past":
            return queryset.filter(date__lt=date.today())


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "date",
        "is_at_min_capacity",
        "is_at_max_capacity",
    )
    inlines = [ParticipantInline]
    list_filter = (UpcomingEventFilter,)

    def is_at_max_capacity(self, obj):
        if obj.max_participants:
            return obj.participant_set.count() >= obj.max_participants
        return False

    is_at_max_capacity.boolean = True
    is_at_max_capacity.short_description = "At Max Capacity?"

    def is_at_min_capacity(self, obj):
        return obj.participant_set.count() >= obj.min_participants

    is_at_min_capacity.boolean = True
    is_at_min_capacity.short_description = "At Min Capacity?"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ("display_name", "event")
