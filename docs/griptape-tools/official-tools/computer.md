# Computer

This tool enables LLMs to execute Python code and run shell commands inside a Docker container. You have to have the Docker daemon running in order for this tool to work.

You can specify a local working directory and environment variables during tool initialization:

```python
--8<-- "docs/griptape-tools/official-tools/src/computer_1.py"
```
```
❮ poetry run python src/docs/task-memory.py
[08/12/24 15:13:56] INFO     ToolkitTask 203ee958d1934811afe0bb86fb246e86
                             Input: Make 2 files and then list the files in the current directory
[08/12/24 15:13:58] INFO     Subtask eb4e843b6f37498f9f0e85ada68114ac
                             Actions: [
                               {
                                 "tag": "call_S17vPQsMCqWY1Lt5x8NtDnTK",
                                 "name": "Computer",
                                 "path": "execute_command",
                                 "input": {
                                   "values": {
                                     "command": "touch file1.txt file2.txt"
                                   }
                                 }
                               }
                             ]
                    INFO     Subtask eb4e843b6f37498f9f0e85ada68114ac
                             Response: Tool returned an empty value
[08/12/24 15:13:59] INFO     Subtask 032770e7697d44f6a0c8559bfea60420
                             Actions: [
                               {
                                 "tag": "call_n61SVDYUGWTt681BaDSaHgt1",
                                 "name": "Computer",
                                 "path": "execute_command",
                                 "input": {
                                   "values": {
                                     "command": "ls"
                                   }
                                 }
                               }
                             ]
                    INFO     Subtask 032770e7697d44f6a0c8559bfea60420
                             Response: file1.txt
                             file2.txt
[08/12/24 15:14:00] INFO     ToolkitTask 203ee958d1934811afe0bb86fb246e86
                             Output: file1.txt, file2.txt
```  
