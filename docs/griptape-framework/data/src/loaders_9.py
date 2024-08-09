from griptape.loaders import EmailLoader

loader = EmailLoader(imap_url="an.email.server.hostname", username="username", password="password")

loader.load(EmailLoader.EmailQuery(label="INBOX"))

loader.load_collection([EmailLoader.EmailQuery(label="INBOX"), EmailLoader.EmailQuery(label="SENT")])
