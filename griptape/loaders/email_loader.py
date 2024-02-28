from __future__ import annotations

from typing import Optional
import logging
import imaplib

from attr import astuple, define, field

from griptape.utils import execute_futures_dict, import_optional_dependency, str_to_hash
from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.loaders import BaseLoader


@define
class EmailLoader(BaseLoader):
    @define(frozen=True)
    class EmailQuery:
        """An email retrieval query

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
        return self._retrieve_email(source)

    def load_collection(self, sources: list[EmailQuery], *args, **kwargs) -> dict[str, ListArtifact | ErrorArtifact]:
        return execute_futures_dict(
            {
                str_to_hash(str(source)): self.futures_executor.submit(self._retrieve_email, source)
                for source in set(sources)
            }
        )

    def _retrieve_email(self, query: EmailQuery) -> ListArtifact | ErrorArtifact:
        mailparser = import_optional_dependency("mailparser")
        label, key, search_criteria, max_count = astuple(query)

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
                    result, data = client.fetch(str(i), "(RFC822)")

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

    def _count_messages(self, message_numbers: bytes):
        return len(list(filter(None, message_numbers.decode().split(" "))))
