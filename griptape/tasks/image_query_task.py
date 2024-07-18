from __future__ import annotations

from typing import Callable

from attrs import define, field

from griptape.artifacts import ImageArtifact, ListArtifact, TextArtifact
from griptape.engines import ImageQueryEngine
from griptape.tasks import BaseTask
from griptape.utils import J2


@define
class ImageQueryTask(BaseTask):
    """A task that executes a natural language query on one or more input images.

    Accepts a text prompt and a list of
    images as input in one of the following formats:
    - tuple of (template string, list[ImageArtifact])
    - tuple of (TextArtifact, list[ImageArtifact])
    - Callable that returns a tuple of (TextArtifact, list[ImageArtifact]).

    Attributes:
        image_query_engine: The engine used to execute the query.
    """

    _image_query_engine: ImageQueryEngine = field(default=None, kw_only=True, alias="image_query_engine")
    _input: (
        tuple[str, list[ImageArtifact]]
        | tuple[TextArtifact, list[ImageArtifact]]
        | Callable[[BaseTask], ListArtifact]
        | ListArtifact
    ) = field(default=None, alias="input")

    @property
    def input(self) -> ListArtifact:
        if isinstance(self._input, ListArtifact):
            return self._input
        elif isinstance(self._input, tuple):
            if isinstance(self._input[0], TextArtifact):
                query_text = self._input[0]
            else:
                query_text = TextArtifact(J2().render_from_string(self._input[0], **self.full_context))

            return ListArtifact([query_text, *self._input[1]])
        elif isinstance(self._input, Callable):
            return self._input(self)
        else:
            raise ValueError(
                "Input must be a tuple of a TextArtifact and a list of ImageArtifacts or a callable that "
                "returns a tuple of a TextArtifact and a list of ImageArtifacts.",
            )

    @input.setter
    def input(
        self,
        value: (
            tuple[str, list[ImageArtifact]]
            | tuple[TextArtifact, list[ImageArtifact]]
            | Callable[[BaseTask], ListArtifact]
        ),
    ) -> None:
        self._input = value

    @property
    def image_query_engine(self) -> ImageQueryEngine:
        if self._image_query_engine is None:
            if self.structure is not None:
                self._image_query_engine = ImageQueryEngine(image_query_driver=self.structure.config.image_query_driver)
            else:
                raise ValueError("Image Query Engine is not set.")
        return self._image_query_engine

    @image_query_engine.setter
    def image_query_engine(self, value: ImageQueryEngine) -> None:
        self._image_query_engine = value

    def run(self) -> TextArtifact:
        query = self.input.value[0]

        if all(isinstance(artifact, ImageArtifact) for artifact in self.input.value[1:]):
            image_artifacts = [
                image_artifact for image_artifact in self.input.value[1:] if isinstance(image_artifact, ImageArtifact)
            ]
        else:
            raise ValueError("All inputs after the query must be ImageArtifacts.")

        self.output = self.image_query_engine.run(query.value, image_artifacts)

        return self.output
