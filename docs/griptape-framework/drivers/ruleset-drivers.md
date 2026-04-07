---
search:
  boost: 2
---

## Overview

Ruleset Drivers can be used to load rules in from external sources.

## Ruleset Drivers

### Local

The [LocalRulesetDriver](../../reference/griptape/drivers/ruleset/local_ruleset_driver.md) allows you to load a Ruleset from a local JSON file. The `persist_dir` parameter is used to specify a local directory where one or more Ruleset files are located. If no `persist_dir` parameter is given, the `.load` method is a no-op.

```python
--8<-- "docs/griptape-framework/drivers/src/local_ruleset_driver.py"
```

### Griptape Cloud

The [GriptapeCloudRulesetDriver](../../reference/griptape/drivers/ruleset/griptape_cloud_ruleset_driver.md) allows you to load a Griptape Cloud Ruleset resource. `Ruleset.name` is used to try and find a Griptape Cloud Ruleset with that alias.

```python
--8<-- "docs/griptape-framework/drivers/src/griptape_cloud_ruleset_driver.py"
```
