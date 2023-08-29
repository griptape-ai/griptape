class TestEmailClient:
    """
    https://docs.griptape.ai/en/latest/griptape-tools/official-tools/email-client/
    """

    def test_email_client(self):
        import os
        from griptape.tools import EmailClient

        client = EmailClient(
            smtp_host=os.environ.get("SMTP_HOST"),
            smtp_port=int(os.environ.get("SMTP_PORT", 465)),
            smtp_password=os.environ.get("SMTP_PASSWORD"),
            smtp_user=os.environ.get("FROM_EMAIL"),
            smtp_use_ssl=bool(os.environ.get("SMTP_USE_SSL")),
        )

        assert client is not None
