from abc import ABC, abstractmethod

from attr import define


@define
class BaseImageGenerationModelDriver(ABC):
    @abstractmethod
    def get_generated_image(self, response: dict) -> bytes:
        ...
