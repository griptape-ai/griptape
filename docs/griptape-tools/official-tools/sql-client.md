# SqlClient

This tool enables LLMs to execute SQL statements via [SQLAlchemy](https://www.sqlalchemy.org/). Depending on your underlying SQL engine, [configure](https://docs.sqlalchemy.org/en/20/core/engines.html) your `engine_url` and give the LLM a hint about what engine you are using via `engine_name`, so that it can create engine-specific statements.

```python
--8<-- "docs/griptape-tools/official-tools/src/sql_client_1.py"
```
```
[09/11/23 17:02:55] INFO     Task d8331f8705b64b4b9d9a88137ed73f3f              
                             Input: SELECT * FROM people;                       
[09/11/23 17:03:02] INFO     Subtask 46c2f8926ce9469e9ca6b1b3364e3e41           
                             Thought: The user wants to retrieve all records    
                             from the 'people' table. I can use the SqlClient   
                             tool to execute this query.                        
                                                                                
                             Action: {"name": "SqlClient",      
                             "path": "execute_query", "input": {"values":   
                             {"sql_query": "SELECT * FROM people;"}}}           
[09/11/23 17:03:03] INFO     Subtask 46c2f8926ce9469e9ca6b1b3364e3e41           
                             Response: Output of "SqlClient.execute_query"   
                             was stored in memory with memory_name              
                             "TaskMemory" and artifact_namespace            
                             "217715ba3e444e4985bee223df5716a8"                 
[09/11/23 17:03:11] INFO     Subtask e51f05449647482caa3051378ab5cb8c           
                             Thought: The output of the SQL query has been      
                             stored in memory. I can retrieve this data using   
                             the TaskMemory's 'summarize' activity.
                             Action: {"name": "TaskMemoryClient", "path":   
                             "summarize", "input": {"values": {"memory_name":   
                             "TaskMemory", "artifact_namespace":                
                             "217715ba3e444e4985bee223df5716a8"}}}                  
[09/11/23 17:03:12] INFO     Subtask e51f05449647482caa3051378ab5cb8c           
                             Response: The text includes a list of employees 
                             with their respective IDs, names, positions. There 
                             are two employees named Tanya Cooley who are both  
                             managers, and two employees named John Doe who are 
                             both coders.                                       
[09/11/23 17:03:17] INFO     Task d8331f8705b64b4b9d9a88137ed73f3f              
                             Output: The 'people' table contains records of     
                             several employees. Notably, there are two employees
                             named Tanya Cooley who are both managers, and two  
                             employees named John Doe who are both coders. 
```
