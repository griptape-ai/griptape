# GoogleDocsClient

The GoogleDocsClient tool provides a way to interact with the Google Docs API. It can be used to create new documents, save content to existing documents, and more.

```python
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
        "client_x509_cert_url": os.environ["GOOGLE_CERT_URL"]
    },
    owner_email=os.environ["GOOGLE_OWNER_EMAIL"],
    off_prompt=False
)

# Set up an agent using the GoogleDocsClient tool
agent = Agent(
    tools=[google_docs_tool]
)

# Task: Create a new Google Doc and save content to it
agent.run(
    "Create doc with name 'test_creation' in test folder with content 'Hey, Tony.",
)
```
```
[10/05/23 12:56:19] INFO     ToolkitTask 90721b7478a74618a63d852d35be3b18       
                             Input: Create doc with name 'test_creation' in     
                             test folder with content 'Hey, Tony.'             
[10/05/23 12:56:28] INFO     Subtask 042b7050755f43578bba2c315d124fcb           
                             Thought: The user wants to create a Google Doc     
                             named 'test_creation' in a folder named 'test'    
                             with the content 'Hey, Tony.'. I can use the       
                             'save_content_to_google_doc' activity of the       
                             GoogleDocsClient tool to achieve this.             
                                                                                
                             Action: {"name":                   
                             "GoogleDocsClient", "path":                    
                             "save_content_to_google_doc", "input": {"values":  
                             {"file_path": "test_creation", "content": "Hey,    
                             Tony.", "folder_path": "test"}}}                  
[10/05/23 12:56:31] INFO     Subtask 042b7050755f43578bba2c315d124fcb           
                             Response: Content has been successfully saved to
                             Google Doc with ID:                                
                             1OgKbsPqxOnzkf65kodb1i1_qC1zjX_Bend5XL5bVxpA.      
[10/05/23 12:56:38] INFO     ToolkitTask 90721b7478a74618a63d852d35be3b18       
                             Output: The document 'test_creation' has been      
                             successfully created in the 'test' folder with the
                             content 'Hey, Tony.'. The Google Doc ID is         
                             1OgKbsPqxOnzkf65kodb1i1_qC1zjX_Bend5XL5bVxpA.     
```