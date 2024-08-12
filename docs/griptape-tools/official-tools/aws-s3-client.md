# AwsS3Client

This tool enables LLMs to make AWS S3 API requests.

```python
--8<-- "docs/griptape-tools/official-tools/src/aws_s3_client_1.py"
```
```
[08/12/24 14:51:36] INFO     ToolkitTask bfc329ebc7d34497b429ab0d18ff7e7b
                             Input: List all my S3 buckets.
[08/12/24 14:51:37] INFO     Subtask dfd07f9e204c4a3d8f55ca3eb9d37ec5
                             Actions: [
                               {
                                 "tag": "call_pZQ05Zmm6lSbEcvPWt4XEDj6",
                                 "name": "AwsS3Client",
                                 "path": "list_s3_buckets",
                                 "input": {
                                   "values": {}
                                 }
                               }
                             ]
                    INFO     Subtask dfd07f9e204c4a3d8f55ca3eb9d37ec5
                             Response: {'Name': 'dummy-bucket-1', 'CreationDate': datetime.datetime(2023, 9, 14, 15, 41, 46,
                             tzinfo=tzutc())}

                             {'Name': 'dummy-bucket-2', 'CreationDate': datetime.datetime(2023, 9, 14, 15, 40, 33, tzinfo=tzutc())}

                             {'Name': 'dummy-bucket-3', 'CreationDate': datetime.datetime(2023, 6, 23, 20, 19, 53, tzinfo=tzutc())}

                             {'Name': 'dummy-bucket-4', 'CreationDate': datetime.datetime(2023, 8, 19, 17, 17, 13, tzinfo=tzutc())}

                             {'Name': 'dummy-bucket-5', 'CreationDate': datetime.datetime(2024, 2, 15, 23, 17, 21, tzinfo=tzutc())}
[08/12/24 14:51:43] INFO     ToolkitTask bfc329ebc7d34497b429ab0d18ff7e7b
                             Output: Here are all your S3 buckets:

                             1. dummy-bucket-1 (Created on 2023-09-14)
                             2. dummy-bucket-2 (Created on 2023-09-14)
                             3. dummy-bucket-3 (Created on 2023-06-23)
                             4. dummy-bucket-4 (Created on 2023-08-19)
                             5. dummy-bucket-5 (Created on 2024-02-15)
```
