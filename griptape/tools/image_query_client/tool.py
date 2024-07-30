from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

from attrs import Factory, define, field
from schema import Literal, Schema

from griptape.artifacts import BlobArtifact, ErrorArtifact, ImageArtifact, TextArtifact
from griptape.loaders import ImageLoader
from griptape.tools import BaseTool
from griptape.utils import load_artifact_from_memory
from griptape.utils.decorators import activity

if TYPE_CHECKING:
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
                },
            ),
        },
    )
    def query_image_from_disk(self, params: dict) -> TextArtifact | ErrorArtifact:
        query = params["values"]["query"]
        image_paths = params["values"]["image_paths"]

        image_artifacts = []
        for image_path in image_paths:
            image_artifacts.append(self.image_loader.load(Path(image_path).read_bytes()))

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
                    Literal("image_artifacts", description="Image artifact memory references."): [
                        {"image_artifact_namespace": str, "image_artifact_name": str},
                    ],
                    "memory_name": str,
                },
            ),
        },
    )
    def query_images_from_memory(self, params: dict[str, Any]) -> TextArtifact | ErrorArtifact:
        query = params["values"]["query"]
        image_artifact_references = params["values"]["image_artifacts"]
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
            except ValueError:
                # If we're unable to parse the artifact as an ImageArtifact, attempt to
                # parse a BlobArtifact and load it as an ImageArtifact.
                blob_artifact = load_artifact_from_memory(
                    memory,
                    image_artifact_reference["image_artifact_namespace"],
                    image_artifact_reference["image_artifact_name"],
                    BlobArtifact,
                )

                image_artifacts.append(self.image_loader.load(blob_artifact.value))
            except Exception as e:
                return ErrorArtifact(str(e))

        return self.image_query_engine.run(query, image_artifacts)
