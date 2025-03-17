from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import schema
from attrs import Factory, define, field

from griptape.artifacts import BaseArtifact, ErrorArtifact, TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


@define
class DateTimeTool(BaseTool):
    denylist: list[str] = field(default=Factory(lambda: ["get_relative_datetime"]), kw_only=True)

    @activity(config={"description": "Can be used to return current date and time."})
    def get_current_datetime(self) -> BaseArtifact:
        return TextArtifact(str(datetime.now()))

    @activity(
        config={
            "description": "Can be used to return a relative date and time.",
            "schema": schema.Schema(
                {
                    schema.Literal(
                        "relative_date_string",
                        description='Relative date in English compatible with the dateparser library. For example, "now EST", "20 minutes ago", '
                        '"in 2 days", "3 months, 1 week and 1 day ago", or "yesterday at 2pm"',
                    ): str,
                },
            ),
        },
    )
    def get_relative_datetime(self, params: dict) -> BaseArtifact:
        from dateparser import parse

        try:
            date_string = params["values"]["relative_date_string"]
            relative_datetime = parse(date_string)

            if relative_datetime:
                return TextArtifact(str(relative_datetime))
            return ErrorArtifact("invalid date string")
        except Exception as e:
            return ErrorArtifact(f"error getting current datetime: {e}")

    @activity(
        config={
            "description": "Can be used to add a timedelta to a datetime.",
            "schema": schema.Schema(
                {
                    schema.Literal(
                        "timedelta_kwargs",
                        description='A dictionary of keyword arguments to pass to the timedelta function. For example, {"days": -1, "hours": 2}',
                    ): dict,
                    schema.Optional(
                        schema.Literal(
                            "iso_datetime",
                            description='Datetime represented as a string in ISO 8601 format. For example, "2021-01-01T00:00:00". Defaults to the current datetime if not provided.',
                        )
                    ): str,
                },
            ),
        },
    )
    def add_timedelta(self, timedelta_kwargs: dict, iso_datetime: Optional[str] = None) -> BaseArtifact:
        if iso_datetime is None:
            iso_datetime = datetime.now().isoformat()
        return TextArtifact((datetime.fromisoformat(iso_datetime) + timedelta(**timedelta_kwargs)).isoformat())

    @activity(
        config={
            "description": "Can be used to calculate the difference between two datetimes. The difference is calculated as end_datetime - start_datetime.",
            "schema": schema.Schema(
                {
                    schema.Literal(
                        "start_datetime",
                        description='Datetime represented as a string in ISO 8601 format. For example, "2021-01-01T00:00:00"',
                    ): str,
                    schema.Literal(
                        "end_datetime",
                        description='Datetime represented as a string in ISO 8601 format. For example, "2021-01-02T00:00:00"',
                    ): str,
                }
            ),
        }
    )
    def get_datetime_diff(self, start_datetime: str, end_datetime: str) -> BaseArtifact:
        return TextArtifact(str(datetime.fromisoformat(end_datetime) - datetime.fromisoformat(start_datetime)))
