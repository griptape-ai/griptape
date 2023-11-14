from abc import ABC, abstractmethod


class BasePromptStackProcessor(ABC):
    @abstractmethod
    def before_run(self, prompt):
        ...

    @abstractmethod
    def after_run(self, result):
        ...
