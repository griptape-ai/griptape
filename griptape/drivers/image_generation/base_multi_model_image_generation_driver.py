from abc import abstractmethod
from typing import Optional, TYPE_CHECKING
from attr import field, define
from griptape.artifacts import ImageArtifact
from .base_image_generation_driver import BaseImageGenerationDriver

if TYPE_CHECKING:
    from griptape.drivers import BaseImageGenerationModelDriver


@define
class BaseMultiModelImageGenerationDriver(BaseImageGenerationDriver):
    image_generation_model_driver: BaseImageGenerationModelDriver = field(kw_only=True)

    @abstractmethod
    def try_generate_image(self, prompts: list[str], negative_prompts: Optional[list[str]] = None) -> ImageArtifact:
        ...
