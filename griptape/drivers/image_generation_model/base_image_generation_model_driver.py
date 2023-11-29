from abc import abstractmethod, ABC
from typing import Optional

from attr import define


@define
class BaseImageGenerationModelDriver(ABC):
    @abstractmethod
    def text_to_image_request_parameters(
        self,
        prompts: list[str],
        image_width: int,
        image_height: int,
        negative_prompts: Optional[list[str]] = None,
        seed: Optional[int] = None,
    ) -> dict:
        ...

    @abstractmethod
    def get_generated_image(self, response: dict) -> bytes:
        ...
