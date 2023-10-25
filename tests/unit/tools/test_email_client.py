from griptape.tools import EmailClient


class TestEmailClient:
    def test_retrieve(self):
        value = {
            "label": "label_test",
            "key": "key_test",
            "search_criteria": "search_test",
        }

        assert (
            "error retrieving email"
            in EmailClient(imap_url="", imap_user="", imap_password="")
            .retrieve({"values": value})
            .value
        )

    def test_send(self):
        value = {"to": "foo@bar.com", "subject": "test", "body": "hello"}

        assert (
            "error sending email"
            in EmailClient(smtp_host="", smtp_port=0)
            .send({"values": value})
            .value
        )
