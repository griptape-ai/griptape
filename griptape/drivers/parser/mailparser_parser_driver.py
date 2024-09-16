from __future__ import annotations

from attrs import define

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseParserDriver
from griptape.utils import import_optional_dependency


@define
class MailparserParserDriver(BaseParserDriver[ListArtifact[TextArtifact]]):
    def try_parse(self, data: list[bytes], meta: dict) -> ListArtifact[TextArtifact]:
        mailparser = import_optional_dependency("mailparser")
        artifacts = []
        for byte in data:
            message = mailparser.parse_from_bytes(byte)

            # Note: mailparser only populates the text_plain field
            # if the message content type is explicitly set to 'text/plain'.
            if message.text_plain:
                artifacts.append(TextArtifact("\n".join(message.text_plain)))

        return ListArtifact(artifacts)
