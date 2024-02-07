from __future__ import annotations

from typing import Any, cast

from attr import define, field, Factory
from schema import Schema, Literal

from griptape.artifacts import TextArtifact, ImageArtifact, ErrorArtifact
from griptape.loaders import ImageLoader
from griptape.tools import BaseTool
from griptape.utils import load_artifact_from_memory
from griptape.utils.decorators import activity
from griptape.engines import ImageQueryEngine


@define
class ImageQueryClient(BaseTool):
    image_query_engine: ImageQueryEngine = field(kw_only=True)
    image_loader: ImageLoader = field(default=Factory(lambda: ImageLoader()), kw_only=True)

    @activity(
        config={
            "description": "This tool can be used to query the contents of images on disk.",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="A detailed question to be answered using the contents of the provided images.",
                    ): str,
                    Literal("image_paths", description="The paths to an image files on disk."): list[str],
                }
            ),
        }
    )
    def query_image_from_disk(self, params: dict) -> TextArtifact | ErrorArtifact:
        query = params["values"]["query"]
        image_paths = params["values"]["image_paths"]

        image_artifacts = []
        for image_path in image_paths:
            with open(image_path, "rb") as f:
                image_artifacts.append(self.image_loader.load(f.read()))

        return self.image_query_engine.run(query, image_artifacts)

    @activity(
        config={
            "description": "This tool can be used to query the contents of images in memory.",
            "schema": Schema(
                {
                    Literal(
                        "query",
                        description="A detailed question to be answered using the contents of the provided images.",
                    ): str,
                    Literal("image_artifact_references", description="Image artifact memory references."): [
                        {
                            Literal(
                                "image_artifact_namespace", description="The namespace of the image artifact in memory."
                            ): str,
                            Literal(
                                "image_artifact_name", description="The name of the image artifact in memory."
                            ): str,
                        }
                    ],
                    "memory_name": str,
                }
            ),
        }
    )
    def query_images_from_memory(self, params: dict[str, Any]) -> TextArtifact | ErrorArtifact:
        query = params["values"]["query"]
        image_artifact_references = params["values"]["image_artifact_references"]
        memory = self.find_input_memory(params["values"]["memory_name"])

        if memory is None:
            return ErrorArtifact("memory not found")

        image_artifacts = []
        for image_artifact_reference in image_artifact_references:
            try:
                image_artifact = load_artifact_from_memory(
                    memory,
                    image_artifact_reference["image_artifact_namespace"],
                    image_artifact_reference["image_artifact_name"],
                    ImageArtifact,
                )

                image_artifacts.append(cast(ImageArtifact, image_artifact))
            except ValueError as e:
                return ErrorArtifact(str(e))

        return self.image_query_engine.run(query, image_artifacts)
