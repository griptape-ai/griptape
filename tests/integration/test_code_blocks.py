import os
import subprocess

import pytest

SKIP_FILES = [
    "docs/griptape-tools/official-tools/src/computer_1.py",
    "docs/examples/src/load_query_and_chat_marqo_1.py",
    "docs/griptape-framework/drivers/src/embedding_drivers_2.py",
    "docs/griptape-framework/drivers/src/embedding_drivers_6.py",
    "docs/griptape-framework/drivers/src/embedding_drivers_7.py",
    "docs/griptape-framework/drivers/src/image_generation_drivers_7.py",
    "docs/griptape-framework/drivers/src/image_generation_drivers_8.py",
    "docs/griptape-framework/drivers/src/image_generation_drivers_9.py",
    "docs/griptape-framework/drivers/src/prompt_drivers_4.py",
    "docs/griptape-framework/drivers/src/prompt_drivers_12.py",
    "docs/griptape-framework/drivers/src/prompt_drivers_14.py",
    "docs/griptape-framework/drivers/src/observability_drivers_1.py",
    "docs/griptape-framework/drivers/src/observability_drivers_2.py",
    "docs/griptape-framework/structures/src/observability_1.py",
    "docs/griptape-framework/structures/src/observability_2.py",
]


def discover_python_files(directory):
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                python_files.append(
                    pytest.param(path, marks=pytest.mark.skipif(path in SKIP_FILES, reason="Skip file"))
                )
    return python_files


@pytest.mark.parametrize("python_file", discover_python_files("docs"))
def test_python_file_execution(python_file):
    """Test that the Python file executes successfully."""
    result = subprocess.run(
        ["poetry", "run", "python", python_file],
        capture_output=True,
        text=True,
        input="Hi\nexit\n",
    )

    assert result.returncode == 0, f"Execution failed for {python_file} with error: {result.stderr}"
