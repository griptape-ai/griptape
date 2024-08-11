---
search:
  boost: 2 
---

## Overview

[Audio Transcription Drivers](../../reference/griptape/drivers/audio_transcription/index.md) extract text from spoken audio.

This driver acts as a critical bridge between audio transcription Engines and the underlying models, facilitating the construction and execution of API calls that transform speech into editable and searchable text. Utilized predominantly in applications that support the input of verbal communications, the Audio Transcription Driver effectively extracts and interprets speech, rendering it into a textual format that can be easily integrated into data systems and Workflows.

This capability is essential for enhancing accessibility, improving content discoverability, and automating tasks that traditionally relied on manual transcription, thereby streamlining operations and enhancing efficiency across various industries.

## Audio Transcription Drivers

### OpenAI

The [OpenAI Audio Transcription Driver](../../reference/griptape/drivers/audio_transcription/openai_audio_transcription_driver.md) utilizes OpenAI's sophisticated `whisper` model to accurately transcribe spoken audio into text. This model supports multiple languages, ensuring precise transcription across a wide range of dialects. 

```python
--8<-- "docs/griptape-framework/drivers/src/audio_transcription_drivers_1.py"
```
