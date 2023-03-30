# EmailSenderTool

This tool enables LLMs to send emails.

```python
ToolStep(
    "send an email with a haiku to hello@warpspeed.cc",
    EmailSenderTool(
        host="localhost",
        port=1025,
        from_email="hello@warpspeed.cc",
        use_ssl=False
    )
)
```

For debugging purposes, you can run a local SMTP server that the LLM will send emails to:

```shell
python -m smtpd -c DebuggingServer -n localhost:1025
```

User the `WARPSPEED_EMAIL_SENDER_TOOL_PASSWORD` environment variable to set the password.