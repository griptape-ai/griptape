# AwsIamClient

This tool enables LLMs to make AWS IAM API requests.

```python
--8<-- "docs/griptape-tools/official-tools/src/aws_iam_client_1.py"
```
```
[08/12/24 14:56:59] INFO     ToolkitTask 12345abcd67890efghijk1112131415
                             Input: List all my IAM users
[08/12/24 14:57:00] INFO     Subtask 54321dcba09876fedcba1234567890ab
                             Actions: [
                               {
                                 "tag": "call_OxhQ9ITNIFq0WjkSnOCYAx8h",
                                 "name": "AwsIamClient",
                                 "path": "list_users",
                                 "input": {
                                   "values": {}
                                 }
                               }
                             ]
                    INFO     Subtask 54321dcba09876fedcba1234567890ab
                             Response: {'Path': '/', 'UserName': 'dummy-user-1', 'UserId': 'AIDAAAAAA1111AAAAAA1111', 'Arn':
                             'arn:aws:iam::123456789012:user/dummy-user-1', 'CreateDate': datetime.datetime(2024, 8, 7, 15, 8, 7, tzinfo=tzutc())}

                             {'Path': '/', 'UserName': 'dummy-user-2', 'UserId': 'AIDBBBBBB2222BBBBBB2222', 'Arn':
                             'arn:aws:iam::123456789012:user/dummy-user-2', 'CreateDate': datetime.datetime(2023, 7, 18, 20, 29, 27, tzinfo=tzutc())}

                             {'Path': '/', 'UserName': 'dummy-user-3', 'UserId': 'AIDCCCCCC3333CCCCCC3333', 'Arn':
                             'arn:aws:iam::123456789012:user/dummy-user-3', 'CreateDate': datetime.datetime(2024, 7, 15, 19, 39, 41, tzinfo=tzutc())}

                             {'Path': '/', 'UserName': 'dummy-user-4', 'UserId': 'AIDDDDDDD4444DDDDDD4444', 'Arn':
                             'arn:aws:iam::123456789012:user/dummy-user-4', 'CreateDate': datetime.datetime(2024, 8, 2, 19, 28, 31, tzinfo=tzutc())}

                             {'Path': '/', 'UserName': 'dummy-user-5', 'UserId': 'AIDEEEEE5555EEEEE5555', 'Arn':
                             'arn:aws:iam::123456789012:user/dummy-user-5', 'CreateDate': datetime.datetime(2023, 8, 29, 20, 56, 37, tzinfo=tzutc())}
[08/12/24 14:57:08] INFO     ToolkitTask 12345abcd67890efghijk1112131415
                             Output: Here are all your IAM users:

                             1. **Username:** dummy-user-1
                                - **UserId:** AIDAAAAAA1111AAAAAA1111
                                - **Arn:** arn:aws:iam::123456789012:user/dummy-user-1
                                - **CreateDate:** 2024-08-07

                             2. **Username:** dummy-user-2
                                - **UserId:** AIDBBBBBB2222BBBBBB2222
                                - **Arn:** arn:aws:iam::123456789012:user/dummy-user-2
                                - **CreateDate:** 2023-07-18

                             3. **Username:** dummy-user-3
                                - **UserId:** AIDCCCCCC3333CCCCCC3333
                                - **Arn:** arn:aws:iam::123456789012:user/dummy-user-3
                                - **CreateDate:** 2024-07-15

                             4. **Username:** dummy-user-4
                                - **UserId:** AIDDDDDDD4444DDDDDD4444
                                - **Arn:** arn:aws:iam::123456789012:user/dummy-user-4
                                - **CreateDate:** 2024-08-02

                             5. **Username:** dummy-user-5
                                - **UserId:** AIDEEEEE5555EEEEE5555
                                - **Arn:** arn:aws:iam::123456789012:user/dummy-user-5
                                - **CreateDate:** 2023-08-29
```
