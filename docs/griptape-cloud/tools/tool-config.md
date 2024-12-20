## Overview

Tool repositories require a configuration file which informs Griptape Cloud of your Managed Tool's dependencies and how it needs to build and run.

## Tool Config File Schema

All relative paths are based off of the directory in which the `tool_config.yaml` file is located.

The schema for the configuration file is as follows:

```yaml
version: 1.0
runtime: python3
runtime_version: 3.12
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
  init_tool_function: init_tool
  init_tool_file: tool.py
  tool_file: tool.py
```

### Configuration Fields

#### version

The Tool Config schema version number.

#### runtime

The runtime environment to use for the Tool.

#### runtime_version

The specific version of the runtime environment for the Tool.

#### build (OPTIONAL)

The build-time configuration for the Tool.

- **pre_build_install_script** - The path to your pre_build_install_script, for running during the Tool build prior to dependency installation. This path is relative to the structure configuration file. Or absolute from the repository root if a forward slash is used: `/my-pre-build-install-script.sh`.
- **post_build_install_script** - The path to your post_build_install_script, for running during the Tool build after dependency installation. This path is relative to the structure configuration file. Or absolute from the repository root if a forward slash is used: `/my-post-build-install-script.sh`.
- **requirements_file** - The path to your Tool's requirements.txt file.
- **cache_build_dependencies** - Defines the configuration for caching build dependencies in order to speed up Deployments
  - **enabled** - Defines whether the build dependency caching is on or off
  - **watched_files** - Defines the particular files that will trigger cache invalidation, resulting in a full rebuild of the Tool and dependencies

#### run (REQUIRED)

The run-time configuration for the Tool.

- **tool_file**: The file that contains the Griptape `BaseTool`-derived class. The default value is `tool.py`.
- **init_tool_file**: The file that contains your `init_tool` function. The default value is `tool.py`.
- **init_tool_function**: The function that will be called. The function takes no arguments and returns an instance of your `Tool`.
