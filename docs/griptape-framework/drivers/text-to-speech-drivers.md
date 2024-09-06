---
search:
  boost: 2 
---

## Overview

[Text to Speech Drivers](../../reference/griptape/drivers/text_to_speech/index.md) are used by [Text To Speech Engines](../engines/audio-engines.md) to build and execute API calls to audio generation models.

Provide a Driver when building an [Engine](../engines/audio-engines.md), then pass it to a [Tool](../tools/index.md) for use by an [Agent](../structures/agents.md):

## Text to Speech Drivers

### Eleven Labs

The [Eleven Labs Text to Speech Driver](../../reference/griptape/drivers/text_to_speech/elevenlabs_text_to_speech_driver.md) provides support for text-to-speech models hosted by Eleven Labs. This Driver supports configurations specific to Eleven Labs, like voice selection and output format.

!!! info
    This driver requires the `drivers-text-to-speech-elevenlabs` [extra](../index.md#extras).

```python
--8<-- "docs/griptape-framework/drivers/src/text_to_speech_drivers_1.py"
```

## OpenAI

The [OpenAI Text to Speech Driver](../../reference/griptape/drivers/text_to_speech/openai_text_to_speech_driver.md) provides support for text-to-speech models hosted by OpenAI. This Driver supports configurations specific to OpenAI, like voice selection and output format.

```python
--8<-- "docs/griptape-framework/drivers/src/text_to_speech_drivers_2.py"
```

## Azure OpenAI

The [Azure OpenAI Text to Speech Driver](../../reference/griptape/drivers/text_to_speech/azure_openai_text_to_speech_driver.md) provides support for text-to-speech models hosted in your Azure OpenAI instance. This Driver supports configurations specific to OpenAI, like voice selection and output format.

```python
--8<-- "docs/griptape-framework/drivers/src/text_to_speech_drivers_3.py"
```
