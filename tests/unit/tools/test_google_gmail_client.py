from griptape.tools import GoogleGmailClient


class TestGoogleGmailClient:
    def test_create_draft_email(self):
        value = {
            "to": "recipient@example.com",
            "subject": "stacey's mom",
            "body": "got it going on",
            "attachment_name": ["/test/foo/bar.txt"],
            "memory_name": "test",
            "artifact_namespace": "1234"
        }

        assert "error creating draft email" in GoogleGmailClient(
            service_account_credentials={}, owner_email="tony@griptape.ai"
        ).create_draft_email({"values": value}).value
