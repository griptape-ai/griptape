# Data Lakes

Data Lakes provide a cloud storage solution integrated into Griptape Cloud. Comprised of Bucket and Asset resources, Data Lakes can be accessed using Griptape with the [GriptapeCloudFileManagerDriver](https://github.com/griptape-ai/griptape/blob/main/griptape/drivers/file_manager/griptape_cloud_file_manager_driver.py).

## Buckets

You can [create a Bucket in the Griptape Cloud console](https://cloud.griptape.ai/buckets/create).

## Assets

You can create Assets in the Griptape Cloud console inside of [a specific Bucket](https://cloud.griptape.ai/buckets). File assets are uploaded via the 'Upload' button. Folder assets are created via the 'Create Folder' button.

### Asset Aliases

A combination of an Asset's Bucket ID and Name, this field is a unique identifier for an Asset. Formatted as `<bucket_id>/<asset_name>`.

### Asset Paths

A Data Lake path that can be used as a prefix filter for Assets inside of a Bucket. Ex: Asset Path `foo/` encompasses both `foo/bar.txt` and `foo/baz.txt`.
