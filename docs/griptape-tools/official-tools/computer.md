# Computer

This tool enables LLMs to execute Python code and run shell commands inside a Docker container. You have to have the Docker daemon running in order for this tool to work.

You can specify a local working directory and environment variables during tool initialization:

```python
--8<-- "docs/griptape-tools/official-tools/src/computer_1.py"
```
```
[09/11/23 16:24:15] INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Input: Run this shell command for me: touch        
                             my_new_file.txt                                    
[09/11/23 16:24:21] INFO     Subtask 1ec0f9ea528e44b89eb9d41da0e00856           
                             Thought: The user wants to create a new file named 
                             "my_new_file.txt". I can do this by executing the  
                             shell command "touch my_new_file.txt" using the    
                             Computer tool with the execute_command activity.   
                                                                                
                             Action: {"name": "Computer",       
                             "path": "execute_command", "input": {"values": 
                             {"command": "touch my_new_file.txt"}}}             
[09/11/23 16:24:22] INFO     Subtask 1ec0f9ea528e44b89eb9d41da0e00856           
                             Response: Output of "Computer.execute_command"  
                             was stored in memory with memory_name              
                             "TaskMemory" and artifact_namespace            
                             "54ffbc84a37a497480cab6ab4f904e7e"                 
[09/11/23 16:24:28] INFO     Subtask f3e1b1d09b4c46babda27342680aa770           
                             Thought: The command has been executed and the     
                             output is stored in memory. However, the "touch"   
                             command does not produce any output when it        
                             successfully creates a file. To confirm that the   
                             file was created, I can list the files in the      
                             current directory using the "ls" command.          
                                                                                
                             Action: {"name": "Computer",       
                             "path": "execute_command", "input": {"values": 
                             {"command": "ls"}}}                                
[09/11/23 16:24:29] INFO     Subtask f3e1b1d09b4c46babda27342680aa770           
                             Response: Output of "Computer.execute_command"  
                             was stored in memory with memory_name              
                             "TaskMemory" and artifact_namespace            
                             "82bc4937564e4901b7fc51fced45b643"                 
[09/11/23 16:24:40] INFO     Subtask 36f0bbfdd7974e6cb52766ba21dc64e0           
                             Thought: The output of the "ls" command is stored  
                             in memory. I need to retrieve this output to check 
                             if "my_new_file.txt" is listed, which would confirm
                             that the file was created successfully.
                             Action: {"name": "TaskMemoryClient", "path":   
                             "query", "input": {"values": {"memory_name":   
                             "TaskMemory", "artifact_namespace":                
                             "82bc4937564e4901b7fc51fced45b643", "query": "Is   
                             my_new_file.txt in the list of files?"}}}                    
[09/11/23 16:24:41] INFO     Subtask 36f0bbfdd7974e6cb52766ba21dc64e0           
                             Response: Yes.                                  
[09/11/23 16:24:42] INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Output: The file "my_new_file.txt" has been        
                             successfully created.                              
                    INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Input: Run this shell command for me: echo 'This is
                             the content of the file.' > my_new_file.txt        
[09/11/23 16:24:53] INFO     Subtask a0a3fb162d6d4f3398a98c6d3604a491           
                             Thought: The user wants to write the text 'This is 
                             the content of the file.' into the file            
                             'my_new_file.txt'. I can achieve this by using the 
                             'execute_command' activity of the 'Computer' tool. 
                                                                                
                             Action: {"name": "Computer",       
                             "path": "execute_command", "input": {"values": 
                             {"command": "echo 'This is the content of the      
                             file.' > my_new_file.txt"}}}                       
                    INFO     Subtask a0a3fb162d6d4f3398a98c6d3604a491           
                             Response: Output of "Computer.execute_command"  
                             was stored in memory with memory_name              
                             "TaskMemory" and artifact_namespace            
                             "ec20f2e7ec674e0286c8d1f05d528957"                 
[09/11/23 16:25:00] INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Output: The text 'This is the content of the file.'
                             has been successfully written into                 
                             'my_new_file.txt'.                                 
                    INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Input: Run this shell command for me: cat          
                             my_new_file.txt                                    
[09/11/23 16:25:10] INFO     Task d08009ee983c4286ba10f83bcf3080e6              
                             Output: The content of the file 'my_new_file.txt'  
                             is: 'This is the content of the file.' 
```  
