from griptape.tools import GoogleGmailClient


class TestGoogleGmailClient:
    def test_create_draft_email(self):
        value = {
            "to": "tony@griptape.ai",
            "subject": "stacey's mom",
            "from": "test@test.com",
            "body": "got it going on",
            "inbox_owner": "tony@griptape.ai"
        }
        assert "error creating draft email" in GoogleGmailClient(
            service_account_credentials={}
        ).create_draft_email({"values": value}).value
