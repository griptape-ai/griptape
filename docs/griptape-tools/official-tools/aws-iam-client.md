# AwsIamClient

This tool enables LLMs to make AWS IAM API requests.

```python
--8<-- "docs/griptape-tools/official-tools/src/aws_iam_client_1.py"
```
```
[09/11/23 16:45:45] INFO     Task 890fcf77fb074c9490d5c91563e0c995              
                             Input: List all my IAM users                       
[09/11/23 16:45:51] INFO     Subtask f2f0809ee10d4538972ed01fdd6a2fb8           
                             Thought: To list all IAM users, I can use the      
                             AwsIamClient tool with the list_users activity.    
                             This activity does not require any input.          
                                                                                
                             Action: {"name": "AwsIamClient",   
                             "path": "list_users"}                          
[09/11/23 16:45:52] INFO     Subtask f2f0809ee10d4538972ed01fdd6a2fb8           
                             Response: Output of "AwsIamClient.list_users"   
                             was stored in memory with memory_name              
                             "TaskMemory" and artifact_namespace            
                             "51d22a018a434904a5da3bb8d4f763f7"                 
[09/11/23 16:45:59] INFO     Subtask 8e0e918571544eeebf46de898466c48c           
                             Thought: The output of the list_users activity is  
                             stored in memory. I can retrieve this information  
                             using the TaskMemory tool with the summarize   
                             activity.
                             Action: {"name": "TaskMemoryClient", "path":   
                             "summarize", "input": {"values": {"memory_name":   
                             "TaskMemory", "artifact_namespace":                
                             "51d22a018a434904a5da3bb8d4f763f7"}}}                                                 
[09/11/23 16:46:03] INFO     Subtask 8e0e918571544eeebf46de898466c48c           
                             Response: The text provides information about   
                             two different users in an AWS IAM system. The first
                             user is named "example-user-1" and has a
                             user ID of "AIDASHBEHWJLQV2IOYDHM". The second user
                             is named "example-user-2" and   
                             has a user ID of "AIDASHBEHWJLWHVS76C6X". Both     
                             users have a path of "/", and their ARNs (Amazon   
                             Resource Names) indicate their location in the IAM 
                             system. The first user was created on July 18,     
                             2023, at 20:29:27 UTC, while the second user was   
                             created on August 29, 2023, at 20:56:37 UTC.       
[09/11/23 16:46:13] INFO     Task 890fcf77fb074c9490d5c91563e0c995              
                             Output: There are two IAM users in your AWS        
                             account:                                           
                                                                                
                             1. User "example-user-1" with user ID   
                             "AIDASHBEHWJLQV2IOYDHM", created on July 18, 2023, 
                             at 20:29:27 UTC.                                   
                             2. User "example-user-2" with   
                             user ID "AIDASHBEHWJLWHVS76C6X", created on August 
                             29, 2023, at 20:56:37 UTC.   

```
