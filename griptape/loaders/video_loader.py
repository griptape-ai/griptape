from __future__ import annotations

from typing import cast, TYPE_CHECKING, Optional, Callable

from attrs import define, field, Factory

from concurrent import futures
from griptape.artifacts import ImageArtifact
from griptape.loaders import BaseLoader, ImageLoader
from griptape.utils import import_optional_dependency

if TYPE_CHECKING:
    from cv2 import VideoCapture


@define
class VideoLoader(BaseLoader):
    """Loads an cv.VideoCapture into Image Artifacts.

    Attributes:
        format: If provided, attempts to ensure image artifacts are in this format when loaded.
                For example, when set to 'PNG', loading image.jpg will return an ImageArtifact containing the image
                    bytes in PNG format.
    """

    futures_executor_fn: Callable[[], futures.Executor] = field(
        default=Factory(lambda: lambda: futures.ThreadPoolExecutor()), kw_only=True
    )
    frame_interval: Optional[int] = field(default=None, kw_only=True)
    format: str = field(default=".jpg", kw_only=True)

    def load(self, source: VideoCapture, *args, **kwargs) -> list[ImageArtifact]:
        cv = import_optional_dependency("cv2")
        image_loader = ImageLoader()

        fps = source.get(cv.CAP_PROP_FPS)
        frame_interval = int(fps)  # Number of frames to skip to sample 1 frame per second
        compression_params = [cv.IMWRITE_JPEG_QUALITY, 80]

        image_artifacts = []
        frame_count = 0
        futures_list = []

        with self.futures_executor_fn() as executor:
            while source.isOpened():
                success, frame = source.read()
                if not success:
                    break

                if frame_count % frame_interval == 0:
                    timestamp_ms = source.get(cv.CAP_PROP_POS_MSEC)
                    futures_list.append(
                        executor.submit(
                            self.__process_frame,
                            frame_count,
                            frame,
                            timestamp_ms,
                            image_loader,
                            self.format,
                            compression_params,
                        )
                    )

                frame_count += 1

            results = [future.result() for future in futures.as_completed(futures_list)]
            results.sort(key=lambda x: x[0])
            image_artifacts = [result[1] for result in results]

        source.release()

        return image_artifacts

    def load_collection(self, sources: list[bytes], *args, **kwargs) -> dict[str, ImageArtifact]:
        return cast(dict[str, ImageArtifact], super().load_collection(sources, *args, **kwargs))

    def __process_frame(self, index, frame, timestamp_ms, image_loader, image_format, compression_params):
        cv2 = import_optional_dependency("cv2")

        minutes, seconds = divmod(min(timestamp_ms, 0) / 1000, 60)
        formatted_timestamp = f"{int(minutes):02}:{int(seconds):02}"

        # Compress the frame
        success, frame_bytes = cv2.imencode(image_format, frame, compression_params)
        if not success:
            raise ValueError("Failed to compress frame.")

        frame_bytes = frame_bytes.tobytes()
        image_artifact = image_loader.load(frame_bytes)

        image_artifact.meta = {"timestamp": formatted_timestamp}

        return index, image_artifact
