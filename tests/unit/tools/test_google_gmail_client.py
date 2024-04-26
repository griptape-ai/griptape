from griptape.tools import GoogleGmailClient


class TestGoogleGmailClient:
    def test_create_draft_email(self):
        value = {"subject": "stacey's mom", "from": "test@test.com", "body": "got it going on"}
        assert (
            "error creating draft email"
            in GoogleGmailClient(service_account_credentials={}, owner_email="tony@griptape.ai", off_prompt=False)
            .create_draft_email({"values": value})
            .value
        )
