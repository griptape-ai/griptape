from __future__ import annotations

import random
import typing

from schema import Literal, Optional, Schema

from griptape.artifacts import TextArtifact
from griptape.tools import BaseTool
from griptape.utils.decorators import activity


class RandomNumberGenerator(BaseTool):
    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {Optional(Literal("decimals", description="Number of decimals to round the random number to")): int}
            ),
        }
    )
    def generate(self, params: dict) -> TextArtifact:
        return TextArtifact(str(round(random.random(), params["values"].get("decimals"))))

    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {Optional(Literal("decimals", description="Number of decimals to round the random number to")): int}
            ),
        }
    )
    def generate_with_decimals(self, decimals: typing.Optional[int]) -> TextArtifact:
        return TextArtifact(str(round(random.random(), decimals)))

    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {Optional(Literal("decimals", description="Number of decimals to round the random number to")): int}
            ),
        }
    )
    def generate_with_values(self, values: dict) -> TextArtifact:
        return TextArtifact(str(round(random.random(), values.get("decimals"))))

    @activity(
        config={
            "description": "Can be used to generate random numbers",
            "schema": Schema(
                {Optional(Literal("decimals", description="Number of decimals to round the random number to")): int}
            ),
        }
    )
    def generate_with_kwargs(self, **kwargs) -> TextArtifact:
        return TextArtifact(str(round(random.random(), kwargs.get("decimals"))))


RandomNumberGenerator()
