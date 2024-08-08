---
search:
  boost: 2 
---

## Overview

[Audio Generation Engines](../../reference/griptape/engines/audio/index.md) facilitate audio generation. Audio Generation Engines provides a `run` method that accepts the necessary inputs for its particular mode and provides the request to the configured [Driver](../drivers/text-to-speech-drivers.md).

### Text to Speech

This Engine facilitates synthesizing speech from text inputs.

```python
--8<-- "docs/griptape-framework/engines/src/audio_engines_1.py"
```

### Audio Transcription

The [Audio Transcription Engine](../../reference/griptape/engines/audio/audio_transcription_engine.md) facilitates transcribing speech from audio inputs.

```python
--8<-- "docs/griptape-framework/engines/src/audio_engines_2.py"
```
