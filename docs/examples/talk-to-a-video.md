We can use Google Gemini's [native video input](https://ai.google.dev/gemini-api/docs/vision?lang=python#prompting-video) capabilities to ask questions about [a video](https://www.youtube.com/watch?v=XXuIBHO4qa8).
In this example, we upload a video file using Gemini's file API, and then pass the result using the [GenericArtifact](../reference/griptape/artifacts/generic_artifact.md) to the Agent.
Note that because we are using Gemini-specific features, this will not work with other [Prompt Drivers](../griptape-framework/drivers/prompt-drivers.md).

```python
--8<-- "docs/examples/src/talk_to_a_video_1.py"
```

```
[07/15/24 11:27:17] INFO     PromptTask 765a4a2833a34084b0077fb49c948ace
                             Input: genai.File({
                                 'name': 'files/zzqllezrzmz7',
                                 'display_name': 'griptape-comfyui.mp4',
                                 'mime_type': 'video/mp4',
                                 'sha256_hash': 'ODk5ZDIxMzQwMGZjYTJkNWU3OTY3YjgzZmUxNzg1ZTNmYzc2YTAxMzgxMWIzYWQyMTBjNzM4ODc5MjU1ZmFmNQ==',
                                 'size_bytes': '4667824',
                                 'state': 'ACTIVE',
                                 'uri': 'https://generativelanguage.googleapis.com/v1beta/files/zzqllezrzmz7',
                                 'video_metadata': {'video_duration': '36s'},
                                 'create_time': '2024-07-15T18:27:14.692475Z',
                                 'expiration_time': '2024-07-17T18:27:14.625351853Z',
                                 'update_time': '2024-07-15T18:27:16.179456Z'})

                             Are there any scenes that show a character with earings?
[07/15/24 11:27:21] INFO     PromptTask 765a4a2833a34084b0077fb49c948ace
                             Output: Yes, there are a few scenes that show characters with earrings:

                             * **0:10-0:15:** A woman with short, dark hair and facial tattoos is shown wearing large hoop earrings.
                             * **0:23:** A woman with short, dark hair and facial tattoos is shown wearing large hoop earrings.

                             Let me know if you have any other questions about the video!

                    INFO     PromptTask 765a4a2833a34084b0077fb49c948ace
                             Input: genai.File({
                                 'name': 'files/zzqllezrzmz7',
                                 'display_name': 'griptape-comfyui.mp4',
                                 'mime_type': 'video/mp4',
                                 'sha256_hash': 'ODk5ZDIxMzQwMGZjYTJkNWU3OTY3YjgzZmUxNzg1ZTNmYzc2YTAxMzgxMWIzYWQyMTBjNzM4ODc5MjU1ZmFmNQ==',
                                 'size_bytes': '4667824',
                                 'state': 'ACTIVE',
                                 'uri': 'https://generativelanguage.googleapis.com/v1beta/files/zzqllezrzmz7',
                                 'video_metadata': {'video_duration': '36s'},
                                 'create_time': '2024-07-15T18:27:14.692475Z',
                                 'expiration_time': '2024-07-17T18:27:14.625351853Z',
                                 'update_time': '2024-07-15T18:27:16.179456Z'})

                             What happens in the scene starting at 19 seconds?
[07/15/24 11:27:26] INFO     PromptTask 765a4a2833a34084b0077fb49c948ace
                             Output: At 19 seconds, a futuristic, four-legged robotic vehicle descends from the sky in a misty forest. The vehicle resembles a mechanical
                             spider or insect, with a rounded central body and powerful-looking legs. It hovers slightly above the ground, emitting two bright beams of
                             light from its underside. The scene has a slightly eerie and mysterious atmosphere, with the fog and bare trees adding to the sense of
                             otherworldliness.
```
