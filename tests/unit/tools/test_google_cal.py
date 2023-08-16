from griptape.tools import GoogleCalendarClient


class TestGoogleCalClient:
    def test_get_upcoming_events(self):
        value = {
            "calendar_id": "primary",
            "calendar_owner_email": "tony@griptape.ai",
            "max_events": 10
        }
        assert "error retrieving calendar events" in GoogleCalendarClient(
            service_account_credentials={}
        ).get_upcoming_events({"values": value}).value

    def test_create_event(self):
        value = {
            "calendar_owner_email": "tony@griptape.ai",
            "start_datetime": "2023-07-28T13:00:00",
            "start_time_zone": "America/Los_Angeles",
            "end_datetime": "2023-07-28T14:00:00",
            "end_time_zone": "America/Los_Angeles",
            "title": "could have been an email",
            "description": "why wasn't this an email?",
            "location": "not rto"
        }
        assert "error creating calendar event" in GoogleCalendarClient(
            service_account_credentials={}
        ).create_event({"values": value}).value