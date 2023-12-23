from __future__ import annotations
from attr import astuple, define, field
from griptape import utils
from griptape.artifacts import ErrorArtifact, ListArtifact, TextArtifact
from griptape.loaders import BaseLoader
from typing import Optional
import imaplib
import logging
import mailparser


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
        key: str | None = field(default=None, kw_only=True)
        search_criteria: str | None = field(default=None, kw_only=True)
        max_count: int | None = field(default=None, kw_only=True)

    imap_url: str = field(kw_only=True)
    username: str = field(kw_only=True)
    password: str = field(kw_only=True)

    def load(self, query: EmailQuery) -> ListArtifact:
        return self._retrieve_email(query)

    def load_collection(self, queries: list[EmailQuery]) -> dict[str, ListArtifact | ErrorArtifact]:
        return utils.execute_futures_dict(
            {
                utils.str_to_hash(str(query)): self.futures_executor.submit(self._retrieve_email, query)
                for query in set(queries)
            }
        )

    def _retrieve_email(self, query: EmailQuery) -> ListArtifact | ErrorArtifact:
        label, key, search_criteria, max_count = astuple(query)

        list_artifact = ListArtifact()
        try:
            with imaplib.IMAP4_SSL(self.imap_url) as client:
                client.login(self.username, self.password)

                mailbox = client.select(f'"{label}"', readonly=True)
                if mailbox[0] != "OK":
                    raise Exception(mailbox[1][0].decode())

                if key and search_criteria:
                    _typ, [message_numbers] = client.search(None, key, f'"{search_criteria}"')
                    messages_count = self._count_messages(message_numbers)
                else:
                    messages_count = int(mailbox[1][0])

                top_n = max(0, messages_count - max_count) if max_count else 0
                for i in range(messages_count, top_n, -1):
                    result, data = client.fetch(str(i), "(RFC822)")
                    message = mailparser.parse_from_bytes(data[0][1])
                    # Note: mailparser only populates the text_plain field
                    # if the message content type is explicitly set to 'text/plain'.
                    if message.text_plain:
                        list_artifact.value.append(TextArtifact("\n".join(message.text_plain)))

                client.close()

                return list_artifact
        except Exception as e:
            logging.error(e)
            return ErrorArtifact(f"error retrieving email: {e}")

    def _count_messages(self, message_numbers: bytes):
        return len(list(filter(None, message_numbers.decode().split(" "))))
