import os
import ssl
from typing import Optional
from warpspeed.tools import Tool
import smtplib
from email.message import EmailMessage
from attrs import define, field


@define
class EmailSenderTool(Tool):
    host: str = field(kw_only=True)
    port: int = field(kw_only=True)
    from_email: str = field(kw_only=True)
    use_ssl: bool = field(default=True, kw_only=True)
    password: Optional[str] = field(default=os.getenv("WARPSPEED_EMAIL_SENDER_TOOL_PASSWORD"), kw_only=True)

    def run(self, args: dict[str]) -> str:
        server = smtplib.SMTP(self.host, self.port)

        to_email = args.get("to")
        subject = args.get("subject")
        body = args.get("body")
        msg = EmailMessage()

        msg['Subject'] = subject
        msg['From'] = self.from_email
        msg['To'] = to_email

        try:
            if self.use_ssl:
                server.starttls(context=ssl.create_default_context())

            if self.password:
                server.login(self.from_email, self.password)

            msg.set_content(body)
            server.send_message(msg)

            return "email was successfully sent"
        except Exception as e:
            return f"error sending email: {e}"
        finally:
            server.quit()
