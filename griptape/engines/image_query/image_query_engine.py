from attrs import define, field, Factory

from typing import cast
from griptape.artifacts import ImageArtifact, TextArtifact, ListArtifact
from griptape.common import PromptStack
from griptape.drivers import BasePromptDriver
from griptape.utils import J2


@define
class ImageQueryEngine:
    prompt_driver: BasePromptDriver = field(kw_only=True)
    system_template_generator: J2 = field(default=Factory(lambda: J2("engines/image-query/system.j2")), kw_only=True)

    def run(self, query: str, image_frames: list[ImageArtifact]) -> TextArtifact:
        prompt_stack = PromptStack()
        prompt_stack.add_system_message(self.system_template_generator.render(image_frames=image_frames))
        prompt_stack.add_user_message(ListArtifact([*image_frames, TextArtifact(query)]))
        message = self.prompt_driver.run(prompt_stack)

        return cast(TextArtifact, message.to_artifact())
