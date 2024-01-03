from abc import abstractmethod
from griptape.schemas import BaseSchema


class BaseConfigSchema(BaseSchema):
    class Meta:
        ordered = True

    @abstractmethod
    def make_obj(self, data, **kwargs):
        ...
