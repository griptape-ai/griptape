from __future__ import annotations
import logging
import datetime
from schema import Schema, Literal, Optional
from attr import define
from griptape.artifacts import TextArtifact, ErrorArtifact, InfoArtifact, ListArtifact
from griptape.utils.decorators import activity
from griptape.tools import BaseGoogleClient


@define
class GoogleCalendarClient(BaseGoogleClient):
    CREATE_EVENT_SCOPES = ['https://www.googleapis.com/auth/calendar']
    GET_UPCOMING_EVENTS_SCOPES = ['https://www.googleapis.com/auth/calendar']

    @activity(config={
        "description": "Can be used to get upcoming events from a google calendar",
        "schema": Schema({
            Literal(
                "calendar_id",
                description="id of the google calendar such as 'primary'"
            ): str,
            Literal(
                "calendar_owner_email",
                description="email of the calendar's owner"
            ): str,
            Literal(
                "max_events",
                description="maximum number of events to return"
            ): int
        })
    })
    def get_upcoming_events(self, params: dict) -> ListArtifact | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params["values"]

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=self.GET_UPCOMING_EVENTS_SCOPES
            )
            delegated_credentials = credentials.with_subject(values["calendar_owner_email"])
            service = build('calendar', 'v3', credentials=delegated_credentials)
            now = datetime.datetime.utcnow().isoformat() + 'Z'

            events_result = service.events().list(
                calendarId=values["calendar_id"], timeMin=now,
                maxResults=values['max_events'], singleEvents=True,
                orderBy='startTime').execute()
            events = events_result.get('items', [])

            return ListArtifact(
                [TextArtifact(str(e)) for e in events]
            )
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving calendar events {e}")

    @activity(config={
        "description": "Can be used to create an event on a google calendar",
        "schema": Schema({
            Literal(
                "calendar_owner_email",
                description="email of the calendar's owner"
            ): str,
            Literal(
                "start_datetime",
                description="combined date-time value in string format according to RFC3399 excluding the timezone for when the meeting starts"
            ): str,
            Literal(
                "start_time_zone",
                description="time zone in which the start time is specified in string format according to IANA time zone data base name, such as 'Europe/Zurich'"
            ): str,
            Literal(
                "end_datetime",
                description="combined date-time value in string format according to RFC3399 excluding the timezone for when the meeting ends"
            ): str,
            Literal(
                "end_time_zone",
                description="time zone in which the end time is specified in string format according to IANA time zone data base name, such as 'Europe/Zurich'"
            ): str,
            Literal(
                "title",
                description="title of the event"
            ): str,
            Literal(
                "description",
                description="description of the event"
            ): str,
            Literal(
                "attendees",
                description="list of the email addresses of attendees using 'email' as key"
            ): list,
            Optional(Literal(
                "location",
                description="location of the event"
            )): str
        })
    })
    def create_event(self, params: dict) -> InfoArtifact | ErrorArtifact:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        values = params['values']

        try:
            credentials = service_account.Credentials.from_service_account_info(
                self.service_account_credentials, scopes=self.CREATE_EVENT_SCOPES
            )
            delegated_credentials = credentials.with_subject(values["calendar_owner_email"])
            service = build('calendar', 'v3', credentials=delegated_credentials)

            event = {
                'summary': values['title'],
                'location': values.get('location'),
                'description': values['description'],
                'start': {
                    'dateTime': values['start_datetime'],
                    'timeZone': values['start_time_zone']
                },
                'end': {
                    'dateTime': values['end_datetime'],
                    'timeZone': values['end_time_zone']
                },
                'attendees': values['attendees']
            }
            event = service.events().insert(calendarId='primary', body=event).execute()
            return InfoArtifact(f'A calendar event was successfully created. (Link:{event.get("htmlLink")})')
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error creating calendar event: {e}")