# GoogleDriveClient

The GoogleDriveClient tool provides a way to interact with the Google Drive API. It can be used to save content on Drive, list files, and more.

```python
import os
from griptape.structures import Agent
from griptape.tools import GoogleDriveClient

# Create the GoogleDriveClient tool
google_drive_tool = GoogleDriveClient(
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
)

# Set up an agent using the GoogleDriveClient tool
agent = Agent(
    tools=[google_drive_tool]
)

# Task: Save content to my Google Drive (default directory is root)
agent.run(
    "Save the content 'Hi this is Tony' in a filed named 'hello.txt' to my Drive.",
)
```
```
[10/05/23 10:49:14] INFO     ToolkitTask 2ae3bb7e828744f3a2631c29c6fce001       
                             Input: Save the content 'Hi this is Tony' in a file
                             named 'hello.txt' to my Drive.                     
[10/05/23 10:49:24] INFO     Subtask 381430d881354184ace65af39e0b292b           
                             Thought: The user wants to save the content 'Hi    
                             this is Tony' in a file named 'hello.txt' to Google
                             Drive. I can use the 'save_content_to_drive'       
                             activity of the GoogleDriveClient tool to          
                             accomplish this.                                   
                                                                                
                             Action: {"name":                   
                             "GoogleDriveClient", "path":                   
                             "save_content_to_drive", "input": {"values":       
                             {"path": "hello.txt", "content": "Hi this is       
                             Tony"}}}                                           
[10/05/23 10:49:26] INFO     Subtask 381430d881354184ace65af39e0b292b           
                             Response: saved successfully                    
[10/05/23 10:49:29] INFO     ToolkitTask 2ae3bb7e828744f3a2631c29c6fce001       
                             Output: The content 'Hi this is Tony' has been     
                             successfully saved in a file named 'hello.txt' on  
                             your Google Drive.      
```
