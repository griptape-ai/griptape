from abc import abstractmethod, ABC
from typing import Any, Dict, Optional

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
    ) -> Dict[str, Any]:
        ...

    @abstractmethod
    def get_generated_image(self, response: Dict[str, Any]) -> bytes:
        ...
