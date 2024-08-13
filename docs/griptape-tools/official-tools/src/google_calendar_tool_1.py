import os

from griptape.structures import Agent
from griptape.tools import GoogleCalendarTool

# Create the GoogleCalendarTool tool
google_calendarendar_tool = GoogleCalendarTool(
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

# Set up an agent using the GoogleCalendarTool tool
agent = Agent(tools=[google_calendarendar_tool])

# Task: Get upcoming events from a Google calendar
agent.run(
    "Get me the details of the next upcoming event from my primary calendar.",
)
