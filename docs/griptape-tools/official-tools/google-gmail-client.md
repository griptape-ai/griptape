# GoogleGmailClient

The GoogleGmailClient tool provides a way to interact with the Gmail API. It can be used to create draft emails, send emails, and more.

```python
from griptape.tools import GoogleGmailClient
from griptape.structures import Agent
import os

# Create the GoogleGmailClient tool
gmail_tool = GoogleGmailClient(
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
        "client_x509_cert_url": os.environ["GOOGLE_CERT_URL"]
    },
     owner_email=os.environ["GOOGLE_OWNER_EMAIL"],
    off_prompt=False
)

# Set up an agent using the GoogleGmailClient tool
agent = Agent(
    tools=[gmail_tool]
)

# Task: Create a draft email in GMail
agent.run(
    "Create a draft email in Gmail to example@email.com with the subject 'Test Draft', the body "
    "'This is a test draft email.'",
)
```
```
[10/05/23 13:24:05] INFO     ToolkitTask 1f190f823d584053bfe9942f41b6cb2d       
                             Input: Create a draft email in Gmail to            
                             example@email.com with the subject 'Test Draft',   
                             the body 'This is a test draft email.'             
[10/05/23 13:24:15] INFO     Subtask 7f2cce7e5b0e425ba696531561697b96           
                             Thought: The user wants to create a draft email in 
                             Gmail. I can use the GoogleGmailClient tool with   
                             the create_draft_email activity to accomplish this.
                             I will need to provide the 'to', 'subject', and    
                             'body' values as input.                            
                                                                                
                             Action: {"name":                   
                             "GoogleGmailClient", "path":                   
                             "create_draft_email", "input": {"values": {"to":   
                             "example@email.com", "subject": "Test Draft",      
                             "body": "This is a test draft email."}}}           
[10/05/23 13:24:16] INFO     Subtask 7f2cce7e5b0e425ba696531561697b96           
                             Response: An email draft was successfully       
                             created (ID: r6322867913697829111)                 
[10/05/23 13:24:19] INFO     ToolkitTask 1f190f823d584053bfe9942f41b6cb2d       
                             Output: The draft email has been successfully      
                             created in Gmail with the ID: r6322867913697829111.
```