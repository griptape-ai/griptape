---
search:
  boost: 2
---

## Overview

File Manager Drivers can be used to load and save files with local or external file systems.

You can use File Manager Drivers with Loaders:

```python
--8<-- "docs/griptape-framework/drivers/src/file_manager_driver.py"
```

Or use them independently as shown below for each driver:

## File Manager Drivers

### Griptape Cloud

The [GriptapeCloudFileManagerDriver](../../reference/griptape/drivers/file_manager/griptape_cloud_file_manager_driver.md) allows you to load and save files sourced from Griptape Cloud Asset and Bucket resources.

```python
--8<-- "docs/griptape-framework/drivers/src/griptape_cloud_file_manager_driver.py"
```

### Local

The [LocalFileManagerDriver](../../reference/griptape/drivers/file_manager/local_file_manager_driver.md) allows you to load and save files sourced from a local directory.

```python
--8<-- "docs/griptape-framework/drivers/src/local_file_manager_driver.py"
```

### Amazon S3

!!! info
    This driver requires the `drivers-file-manager-amazon-s3` [extra](../index.md#extras).

The [LocalFile ManagerDriver](../../reference/griptape/drivers/file_manager/amazon_s3_file_manager_driver.md) allows you to load and save files sourced from an Amazon S3 bucket.

```python
--8<-- "docs/griptape-framework/drivers/src/amazon_s3_file_manager_driver.py"
```
