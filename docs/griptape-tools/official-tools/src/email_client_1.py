import os

from griptape.tools import EmailClient

email_client = EmailClient(
    smtp_host=os.environ.get("SMTP_HOST"),
    smtp_port=int(os.environ.get("SMTP_PORT", 465)),
    smtp_password=os.environ.get("SMTP_PASSWORD"),
    smtp_user=os.environ.get("FROM_EMAIL"),
    smtp_use_ssl=bool(os.environ.get("SMTP_USE_SSL")),
)
