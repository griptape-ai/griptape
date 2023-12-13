from abc import abstractmethod
from griptape.schemas import BaseEventSchema


class BaseImageGenerationEventSchema(BaseEventSchema):
    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
