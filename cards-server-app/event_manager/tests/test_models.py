from config.helpers import BaseTestCase
from event_manager.models import Event, Participant


class TestTasks(BaseTestCase):
    def setUp(self):
        super().setUp()

    def given_an_event(self, **kwargs):
        defaults = {
            "name": "Default Event",
            "date": "2023-01-15",
            "venue_name": "Default Venue",
            "cost": "Free",
        }

        # Override defaults with provided kwargs, if any.
        defaults.update(kwargs)

        event = Event.objects.create(**defaults)
        event.refresh_from_db()
        return event

    def given_an_event_participant(self, event, name="Default Participant"):
        return Participant.objects.create(event=event, name=name)

    def test_event_serialization(self):
        event = self.given_an_event(
            name="Sample Event",
            date="2023-01-15",
            time="14:00:00",
            venue_name="Sample Venue",
        )
        self.given_an_event_participant(event, name="Participant 1")
        self.given_an_event_participant(event, name="Participant 2")

        serialized_text = event.serialize_as_text()
        expected_text = """Sample Event on 2023-01-15 14:00 @ Sample Venue
1. Participant 1
2. Participant 2"""

        self.assertEqual(serialized_text, expected_text)

        event2 = self.given_an_event(
            name="Sample Event 2",
            date="2023-01-17",
            venue_name="Sample Venue 2",
        )
        self.given_an_event_participant(event2, name="Participant A")
        self.given_an_event_participant(event2, name="Participant B")

        serialized_text = event2.serialize_as_text()
        expected_text = """Sample Event 2 on 2023-01-17 @ Sample Venue 2
1. Participant A
2. Participant B"""

        self.assertEqual(serialized_text, expected_text)
