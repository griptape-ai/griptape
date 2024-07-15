from __future__ import annotations

import datetime
import logging

from attrs import define, field
from schema import Literal, Optional, Schema

from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact, TextArtifact
from griptape.tools import BaseGoogleClient
from griptape.utils.decorators import activity


@define
class GoogleCalendarClient(BaseGoogleClient):
    CREATE_EVENT_SCOPES = ["https://www.googleapis.com/auth/calendar"]

    GET_UPCOMING_EVENTS_SCOPES = ["https://www.googleapis.com/auth/calendar"]

    owner_email: str = field(kw_only=True)

    @activity(
        config={
            "description": "Can be used to get upcoming events from a google calendar",
            "schema": Schema(
                {
                    Literal("calendar_id", description="id of the google calendar such as 'primary'"): str,
                    Literal("max_events", description="maximum number of events to return"): int,
                },
            ),
        },
    )
    def get_upcoming_events(self, params: dict) -> ListArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(
                scopes=self.GET_UPCOMING_EVENTS_SCOPES,
                service_name="calendar",
                version="v3",
                owner_email=self.owner_email,
            )
            now = datetime.datetime.utcnow().isoformat() + "Z"

            events_result = (
                service.events()
                .list(
                    calendarId=values["calendar_id"],
                    timeMin=now,
                    maxResults=values["max_events"],
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            return ListArtifact([TextArtifact(str(e)) for e in events])
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving calendar events {e}")

    @activity(
        config={
            "description": "Can be used to create an event on a google calendar",
            "schema": Schema(
                {
                    Literal(
                        "start_datetime",
                        description="combined date-time value in string format according to RFC3399 "
                        "excluding the timezone for when the meeting starts",
                    ): str,
                    Literal(
                        "start_time_zone",
                        description="time zone in which the start time is specified in string format "
                        "according to IANA time zone data base name, such as 'Europe/Zurich'",
                    ): str,
                    Literal(
                        "end_datetime",
                        description="combined date-time value in string format according to RFC3399 "
                        "excluding the timezone for when the meeting ends",
                    ): str,
                    Literal(
                        "end_time_zone",
                        description="time zone in which the end time is specified in string format "
                        "according to IANA time zone data base name, such as 'Europe/Zurich'",
                    ): str,
                    Literal("title", description="title of the event"): str,
                    Literal("description", description="description of the event"): str,
                    Literal(
                        "attendees",
                        description="list of the email addresses of attendees using 'email' as key",
                    ): list[str],
                    Optional(Literal("location", description="location of the event")): str,
                },
            ),
        },
    )
    def create_event(self, params: dict) -> InfoArtifact | ErrorArtifact:
        values = params["values"]

        try:
            service = self._build_client(
                scopes=self.CREATE_EVENT_SCOPES,
                service_name="calendar",
                version="v3",
                owner_email=self.owner_email,
            )

            event = {
                "summary": values["title"],
                "location": values.get("location"),
                "description": values["description"],
                "start": {"dateTime": values["start_datetime"], "timeZone": values["start_time_zone"]},
                "end": {"dateTime": values["end_datetime"], "timeZone": values["end_time_zone"]},
                "attendees": values["attendees"],
            }
            event = service.events().insert(calendarId="primary", body=event).execute()
            return InfoArtifact(f'A calendar event was successfully created. (Link:{event.get("htmlLink")})')
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error creating calendar event: {e}")
