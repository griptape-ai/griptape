import os

from griptape.structures import Agent
from griptape.tools import GoogleDocsClient

# Create the GoogleDocsClient tool
google_docs_tool = GoogleDocsClient(
    service_account_credentials={
        "type": os.environ["GOOGLE_ACCOUNT_TYPE"],
        "project_id": os.environ["GOOGLE_PROJECT_ID"],
        "private_key_id": os.environ["GOOGLE_PRIVATE_KEY_ID"],
        "private_key": os.environ["GOOGLE_PRIVATE_KEY"],
        "client_email": os.environ["GOOGLE_CLIENT_EMAIL"],
        "client_id": os.environ["GOOGLE_CLIENT_ID"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ["GOOGLE_CERT_URL"],
    },
    owner_email=os.environ["GOOGLE_OWNER_EMAIL"],
)

# Set up an agent using the GoogleDocsClient tool
agent = Agent(tools=[google_docs_tool])

# Task: Create a new Google Doc and save content to it
agent.run(
    "Create doc with name 'test_creation' in test folder with content 'Hey, Tony.",
)
