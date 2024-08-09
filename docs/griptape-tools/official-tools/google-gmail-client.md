# GoogleGmailClient

The GoogleGmailClient tool provides a way to interact with the Gmail API. It can be used to create draft emails, send emails, and more.

```python
--8<-- "docs/griptape-tools/official-tools/src/google_gmail_client_1.py"
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
