# GoogleDocsClient

The GoogleDocsClient tool provides a way to interact with the Google Docs API. It can be used to create new documents, save content to existing documents, and more.

```python
--8<-- "docs/griptape-tools/official-tools/src/google_docs_client_1.py"
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
