## Overview

Structure repositories require a configuration file which informs Griptape Cloud of your Managed Structure's dependencies and how it needs to build and run.

## Structure Config File Schema

The schema for the configuration file is as follows:

```yaml
version: 1.0
runtime: python3
runtime_version: 3.11
build:
  pre_build_install_script: scripts/my-pre-build-install-script.sh
  post_build_install_script: scripts/my-post-build-install-script.sh
  requirements_file: requirements.txt
  cache_build_dependencies:
    enabled: false
    watched_files:
      - requirements.txt
      - scripts/my-pre-build-install-script.sh
      - scripts/my-post-build-install-script.sh
run:
  main_file: structure.py
```

### Configuration Fields

#### version

The Structure Config schema version number.

#### runtime

The runtime environment to use for the Structure.

#### runtime_version

The specific version of the runtime environment for the Structure.

#### build (OPTIONAL)

The build-time configuration for the Structure.

* **pre_build_install_script** - The path to your pre_build_install_script, for running during the Structure build prior to dependency installation. This path is relative to the structure configuration file. Or absolute from the repository root if a forward slash is used: `/my-pre-build-install-script.sh`.
* **post_build_install_script** - The path to your post_build_install_script, for running during the Structure build after dependency installation. This path is relative to the structure configuration file. Or absolute from the repository root if a forward slash is used: `/my-post-build-install-script.sh`.
* **requirements_file** - The path to your Structure's requirements.txt file.
* **cache_build_dependencies** - Defines the configuration for caching build dependencies in order to speed up Deployments
  * **enabled** - Defines whether the build dependency caching is on or off
  * **watched_files** - Defines the particular files that will trigger cache invalidation, resulting in a full rebuild of the Structure and dependencies

#### run (REQUIRED)

The run-time configuration for the Structure.

* **main_file** - Specifies the path to the entry point file of the Managed Structure. This path is relative to the structure_config.yaml. Or absolute from the repository root if a forward slash is used: `/structure.py`.
