# AwsS3Client

This tool enables LLMs to make AWS S3 API requests.

```python
--8<-- "docs/griptape-tools/official-tools/src/aws_s3_client_1.py"
```
```
[09/11/23 16:49:35] INFO     Task 8bf7538e217a4b5a8472829f5eee75b9              
                             Input: List all my S3 buckets.                     
[09/11/23 16:49:41] INFO     Subtask 9fc44f5c8e73447ba737283cb2ef7f5d           
                             Thought: To list all S3 buckets, I can use the     
                             "list_s3_buckets" activity of the "AwsS3Client"    
                             tool. This activity doesn't require any input.     
                                                                                
                             Action: {"name": "AwsS3Client",    
                             "path": "list_s3_buckets"}                     
[09/11/23 16:49:42] INFO     Subtask 9fc44f5c8e73447ba737283cb2ef7f5d           
                             Response: Output of                             
                             "AwsS3Client.list_s3_buckets" was stored in memory 
                             with memory_name "TaskMemory" and              
                             artifact_namespace                                 
                             "f2592085fd4a430286a46770ea508cc9"                 
[09/11/23 16:49:50] INFO     Subtask 0e9bb639a432431a92ef40a8c085ca0f           
                             Thought: The output of the "list_s3_buckets"       
                             activity is stored in memory. I can retrieve this  
                             information using the "summarize" activity of the  
                             "TaskMemory" tool.
                             Action: {"name": "TaskMemoryClient", "path":   
                             "summarize", "input": {"values": {"memory_name":   
                             "TaskMemory", "artifact_namespace":                
                             "f2592085fd4a430286a46770ea508cc9"}}}                                       
[09/11/23 16:49:52] INFO     Subtask 0e9bb639a432431a92ef40a8c085ca0f           
                             Response: The text consists of multiple         
                             dictionaries, each containing a 'Name' and         
                             'CreationDate' key-value pair. The 'Name'          
                             represents the name of a resource or bucket, while 
                             the 'CreationDate' represents the date and time    
                             when the resource or bucket was created.           
[09/11/23 16:50:03] INFO     Task 8bf7538e217a4b5a8472829f5eee75b9              
                             Output: The names of your S3 buckets are as        
                             follows:                                           
                             1. Bucket Name: 'example-bucket-1', Creation Date: 
                             '2022-01-01T00:00:00Z'                             
                             2. Bucket Name: 'example-bucket-2', Creation Date: 
                             '2022-01-02T00:00:00Z'                             
                             3. Bucket Name: 'example-bucket-3', Creation Date: 
                             '2022-01-03T00:00:00Z'                             
                             Please note that the creation dates are in UTC.  
```
