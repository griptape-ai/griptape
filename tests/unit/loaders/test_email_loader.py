from __future__ import annotations

from email import message
from griptape.artifacts import ErrorArtifact, ListArtifact
from griptape.loaders import EmailLoader
from typing import Optional
import email
import pytest


class TestEmailLoader:
    @pytest.fixture(autouse=True)
    def mock_imap_connection(self, mocker):
        mock_imap_connection = mocker.patch("imaplib.IMAP4_SSL").return_value
        mock_imap_connection.__enter__.return_value = mock_imap_connection
        return mock_imap_connection

    @pytest.fixture
    def mock_login(self, mock_imap_connection):
        return mock_imap_connection.login

    @pytest.fixture(autouse=True)
    def mock_select(self, mock_imap_connection):
        mock_select = mock_imap_connection.select
        mock_select.return_value = to_select_response("OK", 1)
        return mock_select

    @pytest.fixture
    def mock_search(self, mock_imap_connection):
        return mock_imap_connection.search

    @pytest.fixture(autouse=True)
    def mock_fetch(self, mock_imap_connection):
        mock_fetch = mock_imap_connection.fetch
        mock_fetch.return_value = to_fetch_message("message", "text/plain")
        return mock_fetch

    @pytest.fixture
    def loader(self):
        return EmailLoader(imap_url="an.email.server.hostname", username="username", password="password")

    def test_load_accepts_explicit_plain_text(self, loader):
        # When
        list_artifact = loader.load(EmailLoader.EmailQuery(label="INBOX"))

        # Then
        assert to_value_set(list_artifact) == {"message"}

    @pytest.mark.parametrize("content_type", [None, "text/html"])
    def test_load_ignores_content_types(self, loader, mock_fetch, content_type):
        # Given
        mock_fetch.return_value = to_fetch_message("message", content_type)

        # When
        list_artifact = loader.load(EmailLoader.EmailQuery(label="INBOX"))

        # Then
        assert to_value_set(list_artifact) == set()

    @pytest.mark.parametrize("match_count", range(3))
    def test_load_with_search(self, loader, mock_search, mock_fetch, match_count):
        # Given
        mock_search.return_value = to_search_response(match_count)
        mock_fetch.side_effect = [to_fetch_message(f"message-{i}", "text/plain") for i in range(match_count)]

        # When
        list_artifact = loader.load(EmailLoader.EmailQuery(label="INBOX", key="key", search_criteria="search-criteria"))

        # Then
        mock_search.assert_called_once_with(None, "key", '"search-criteria"')
        assert mock_fetch.call_count == match_count
        assert isinstance(list_artifact, ListArtifact)
        assert to_value_set(list_artifact) == {f"message-{i}" for i in range(match_count)}

    def test_load_returns_error_artifact_when_select_returns_non_ok(self, loader, mock_select):
        # Given
        mock_select.return_value = (None, [b"NOT-OK"])

        # When
        artifact = loader.load(EmailLoader.EmailQuery(label="INBOX"))

        # Then
        assert isinstance(artifact, ErrorArtifact)

    def test_load_returns_error_artifact_when_login_throws(self, loader, mock_login):
        # Given
        mock_login.side_effect = Exception("login-failed")

        # When
        artifact = loader.load(EmailLoader.EmailQuery(label="INBOX"))

        # Then
        assert isinstance(artifact, ErrorArtifact)

    def test_load_collection(self, loader, mock_fetch):
        # Given
        mock_fetch.side_effect = [to_fetch_message(f"message-{i}", "text/plain") for i in range(3)]

        # When
        list_artifact_by_hash = loader.load_collection([EmailLoader.EmailQuery(label=f"INBOX-{i}") for i in range(3)])

        # Then
        assert mock_fetch.call_count == 3
        assert to_value_set(list_artifact_by_hash) == {f"message-{i}" for i in range(3)}

    def test_load_collection_skips_duplicate_queries(self, loader, mock_fetch):
        # Given
        mock_fetch.return_value = to_fetch_message("message", "text/plain")

        # When
        list_artifact_by_hash = loader.load_collection([EmailLoader.EmailQuery(label="INBOX")] * 3)

        # Then
        mock_fetch.assert_called_once()
        assert len(list_artifact_by_hash) == 1
        assert to_value_set(list_artifact_by_hash) == {"message"}


def to_search_response(messages_count: int):
    message_numbers = " ".join(["message"] * messages_count).encode()
    return (None, [message_numbers])


def to_select_response(status: str, message_count: int):
    return (status, (str(message_count),))


def to_fetch_message(body: str, content_type: Optional[str]):
    return to_fetch_response(to_message(body, content_type))


def to_fetch_response(message: message):
    return (None, ((None, message.as_bytes()),))


def to_message(body: str, content_type: Optional[str]) -> message:
    message = email.message_from_string(body)
    if content_type:
        message.set_type(content_type)
    return message


def to_value_set(artifact_or_dict: ListArtifact | dict[str, ListArtifact]) -> set[str]:
    if isinstance(artifact_or_dict, ListArtifact):
        return {value.value for value in artifact_or_dict.value}
    elif isinstance(artifact_or_dict, dict):
        return {
            text_artifact.value for list_artifact in artifact_or_dict.values() for text_artifact in list_artifact.value
        }
    else:
        raise Exception
