from griptape.tools import GoogleGmailTool


class TestGoogleGmailTool:
    def test_create_draft_email(self):
        value = {"subject": "stacey's mom", "from": "test@test.com", "body": "got it going on"}
        assert (
            "error creating draft email"
            in GoogleGmailTool(service_account_credentials={}, owner_email="tony@griptape.ai")
            .create_draft_email({"values": value})
            .value
        )
