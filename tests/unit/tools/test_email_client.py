from griptape.artifacts import ErrorArtifact, InfoArtifact, ListArtifact
from griptape.loaders.email_loader import EmailLoader
from griptape.artifacts import TextArtifact
from griptape.tools import EmailClient
import pytest


class TestEmailClient:
    @pytest.fixture(autouse=True)
    def mock_email_loader(self, mocker):
        mock_email_loader = mocker.patch(
            "griptape.tools.email_client.tool.EmailLoader",
            EmailQuery=EmailLoader.EmailQuery,  # Prevents mocking the nested EmailQuery class
        ).return_value
        mock_email_loader.load.return_value = ListArtifact([TextArtifact("fake-email-content")])
        return mock_email_loader

    @pytest.fixture(autouse=True)
    def mock_smtp(self, mocker):
        mock_smtp = mocker.patch("smtplib.SMTP").return_value
        mock_smtp.__enter__.return_value = mock_smtp
        return mock_smtp

    @pytest.fixture(autouse=True)
    def mock_smtp_ssl(self, mocker):
        mock_smtp_ssl = mocker.patch("smtplib.SMTP_SSL").return_value
        mock_smtp_ssl.__enter__.return_value = mock_smtp_ssl
        return mock_smtp_ssl

    @pytest.fixture
    def client(self):
        return EmailClient(
            username="fake-username",
            password="fake-password",
            smtp_host="foobar.com",
            smtp_port=86,
            mailboxes={"INBOX": "default mailbox for incoming email", "SENT": "default mailbox for sent email"},
        )

    @pytest.fixture
    def send_params(self):
        return {"values": {"to": "fake@fake.fake", "subject": "fake-subject", "body": "fake-body"}}

    @pytest.mark.parametrize(
        "values,query",
        [
            ({"label": "fake-label"}, EmailLoader.EmailQuery(label="fake-label")),
            ({"label": "fake-label", "key": "fake-key"}, EmailLoader.EmailQuery(label="fake-label", key="fake-key")),
            (
                {"label": "fake-label", "search_criteria": "fake-search-criteria"},
                EmailLoader.EmailQuery(label="fake-label", search_criteria="fake-search-criteria"),
            ),
            ({"label": "fake-label", "max_count": "32"}, EmailLoader.EmailQuery(label="fake-label", max_count=32)),
        ],
    )
    def test_retrieve(self, client, mock_email_loader, values, query):
        # When
        artifact = client.retrieve({"values": values})

        # Then
        mock_email_loader.load.assert_called_once_with(query)
        assert artifact[0].value == "fake-email-content"

    def test_retrieve_when_email_max_retrieve_count_set(self, mock_email_loader):
        # Given
        client = EmailClient(email_max_retrieve_count=84, mailboxes={"INBOX": "default mailbox for incoming email"})

        # When
        client.retrieve({"values": {"label": "fake-label"}})

        # Then
        mock_email_loader.load.assert_called_once_with(EmailLoader.EmailQuery(label="fake-label", max_count=84))

    @pytest.mark.parametrize(
        "params", [{}, {"values": {}}, {"values": {"label": "fake-label", "max_count": "not-an-int"}}]
    )
    def test_retrieve_throws_when_params_invalid(self, client, params):
        with pytest.raises(Exception) as e:
            client.retrieve(params)

        # Then
        assert isinstance(e.value, Exception)

    def test_send(self, client, send_params):
        # When
        artifact = client.send(send_params)

        # Then
        assert isinstance(artifact, InfoArtifact)
        assert artifact.value == "email was successfully sent"

    def test_send_when_smtp_overrides_set(self, send_params):
        # Given
        client = EmailClient(
            smtp_host="smtp-host",
            smtp_port=86,
            smtp_use_ssl=False,
            smtp_user="smtp-user",
            smtp_password="smtp-password",
        )

        # When
        artifact = client.send(send_params)

        # Then
        assert isinstance(artifact, InfoArtifact)
        assert artifact.value == "email was successfully sent"

    @pytest.mark.parametrize(
        "params",
        [
            {},
            {"values": {}},
            {"values": {"to": "fake@fake.fake", "subject": "fake-subject"}},
            {"values": {"to": "fake@fake.fake", "body": "fake-body"}},
            {"values": {"subject": "fake-subject", "body": "fake-body"}},
        ],
    )
    def test_send_throws_when_params_invalid(self, client, params):
        # When
        with pytest.raises(Exception) as e:
            client.send(params)

        # Then
        assert isinstance(e.value, Exception)

    def test_send_returns_error_artifact_when_sendmail_throws(self, client, mock_smtp_ssl, send_params):
        # Given
        mock_smtp_ssl.sendmail.side_effect = Exception("sendmail-failed")

        # When
        artifact = client.send(send_params)

        # Then
        assert isinstance(artifact, ErrorArtifact)
        assert artifact.value.startswith("error sending email")
