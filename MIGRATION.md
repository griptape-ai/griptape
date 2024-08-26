# Migration Guide

This document provides instructions for migrating your codebase to accommodate breaking changes introduced in new versions of Griptape.

## 0.30.X to 0.31.X

### Exceptions Over `ErrorArtifact`s

Drivers, Loaders, and Engines will now raises exceptions rather than returning `ErrorArtifact`s.
Update any logic that expects `ErrorArtifact` to handle exceptions instead.

```python
# Before
artifacts = WebLoader().load("https://www.griptape.ai")

if isinstance(artifacts, ErrorArtifact):
    raise Exception(artifacts.value)

# After
try:
    artifacts = WebLoader().load("https://www.griptape.ai")
except Exception as e:
    raise e
```
