from __future__ import annotations

import imaplib
import logging
from typing import Optional, Union, cast

from attrs import astuple, define, field

from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.loaders import BaseLoader
from griptape.utils import import_optional_dependency


@define
class EmailLoader(BaseLoader):
    @define(frozen=True)
    class EmailQuery:
        """An email retrieval query.

        Attributes:
            label: Label to retrieve emails from such as 'INBOX' or 'SENT'.
            key: Optional key for filtering such as 'FROM' or 'SUBJECT'.
            search_criteria: Optional search criteria to filter emails by key.
            max_count: Optional max email count.
        """

        label: str = field(kw_only=True)
        key: Optional[str] = field(default=None, kw_only=True)
        search_criteria: Optional[str] = field(default=None, kw_only=True)
        max_count: Optional[int] = field(default=None, kw_only=True)

    imap_url: str = field(kw_only=True)
    username: str = field(kw_only=True)
    password: str = field(kw_only=True)

    def load(self, source: EmailQuery, *args, **kwargs) -> ListArtifact | ErrorArtifact:
        mailparser = import_optional_dependency("mailparser")
        label, key, search_criteria, max_count = astuple(source)

        artifacts = []
        try:
            with imaplib.IMAP4_SSL(self.imap_url) as client:
                client.login(self.username, self.password)

                mailbox = client.select(f'"{label}"', readonly=True)
                if mailbox[0] != "OK":
                    raise Exception(mailbox[1][0].decode())

                if key and search_criteria:
                    _typ, [message_numbers] = client.search(None, key, f'"{search_criteria}"')
                    messages_count = self._count_messages(message_numbers)
                elif len(mailbox) > 1 and mailbox[1] and mailbox[1][0] is not None:
                    messages_count = int(mailbox[1][0])
                else:
                    raise Exception("unable to parse number of messages")

                top_n = max(0, messages_count - max_count) if max_count else 0
                for i in range(messages_count, top_n, -1):
                    _result, data = client.fetch(str(i), "(RFC822)")

                    if data is None or not data or data[0] is None:
                        continue

                    message = mailparser.parse_from_bytes(data[0][1])

                    # Note: mailparser only populates the text_plain field
                    # if the message content type is explicitly set to 'text/plain'.
                    if message.text_plain:
                        artifacts.append(TextArtifact("\n".join(message.text_plain)))

                client.close()

                return ListArtifact(artifacts)
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving email: {e}")

    def _count_messages(self, message_numbers: bytes) -> int:
        return len(list(filter(None, message_numbers.decode().split(" "))))

    def load_collection(self, sources: list[EmailQuery], *args, **kwargs) -> dict[str, ListArtifact | ErrorArtifact]:
        return cast(dict[str, Union[ListArtifact, ErrorArtifact]], super().load_collection(sources, *args, **kwargs))
