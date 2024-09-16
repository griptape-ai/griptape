from __future__ import annotations

import imaplib
from typing import Optional

from attrs import Factory, astuple, define, field

from griptape.artifacts import ListArtifact, TextArtifact
from griptape.drivers import BaseParserDriver, MailparserParserDriver
from griptape.loaders import BaseLoader


@define
class EmailLoader(BaseLoader["EmailLoader.EmailQuery", list[bytes], ListArtifact]):  # pyright: ignore[reportGeneralTypeIssues]
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
    parser_driver: BaseParserDriver[ListArtifact[TextArtifact]] = field(
        default=Factory(lambda: MailparserParserDriver()), kw_only=True
    )

    def fetch(self, source: EmailLoader.EmailQuery) -> tuple[list[bytes], dict]:
        label, key, search_criteria, max_count = astuple(source)

        mail_bytes = []
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

                mail_bytes.append(data[0][1])

            client.close()

        return mail_bytes, {}

    def parse(self, data: list[bytes], meta: dict) -> ListArtifact[TextArtifact]:
        return self.parser_driver.parse(data, meta)

    def _count_messages(self, message_numbers: bytes) -> int:
        return len(list(filter(None, message_numbers.decode().split(" "))))
