# GoogleDriveClient

The GoogleDriveClient tool provides a way to interact with the Google Drive API. It can be used to save content on Drive, list files, and more.

```python
--8<-- "docs/griptape-tools/official-tools/src/google_drive_client_1.py"
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
