# EmailClient

The [EmailClient](../../reference/griptape/tools/email_client/tool.md) enables LLMs to send emails.

```python
--8<-- "docs/griptape-tools/official-tools/src/email_client_1.py"
```

For debugging purposes, you can run a local SMTP server that the LLM can send emails to:

```shell
python -m smtpd -c DebuggingServer -n localhost:1025
```
