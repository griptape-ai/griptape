from __future__ import annotations

from typing import Callable

from attr import define, field

from griptape.artifacts import ImageArtifact, TextArtifact
from griptape.engines import ImageQueryEngine
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class ImageQueryTask(BaseTask):
    image_query_engine: ImageQueryEngine = field(kw_only=True)
    _input: tuple[str, list[ImageArtifact]] | tuple[TextArtifact, list[ImageArtifact]] | Callable[
        [BaseTask], tuple[TextArtifact, list[ImageArtifact]]
    ] = field(default=None)

    @property
    def input(self) -> tuple[TextArtifact, list[ImageArtifact]]:
        if isinstance(self._input, tuple):
            if isinstance(self._input[0], TextArtifact):
                query_text = self._input[0]
            else:
                query_text = TextArtifact(J2().render_from_string(self._input[0], **self.full_context))

            return query_text, self._input[1]
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError(
                "Input must be a tuple of a text artifact and a list of image artifacts or a callable that "
                "returns a tuple of a text artifact and a list of image artifacts."
            )

    @input.setter
    def input(
        self,
        value: tuple[TextArtifact, list[ImageArtifact]]
        | Callable[[BaseTask], tuple[TextArtifact, list[ImageArtifact]]],
    ) -> None:
        self._input = value

    def run(self) -> TextArtifact:
        query = self.input[0]
        image_artifacts = self.input[1]

        response = self.image_query_engine.run(query.value, image_artifacts)

        return response
