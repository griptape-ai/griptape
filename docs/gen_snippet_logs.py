from __future__ import annotations

import concurrent.futures
import os
import re
import subprocess
import sys
from re import Pattern

# This pattern detects an original code block referencing a .py file:
#   ```python
#   --8<-- "path/to/file.py"
#   ```
CODE_BLOCK_PATTERN: Pattern[str] = re.compile(
    r"""```python\n(--8<--\s+\"([^\"]+)\")\n```""",
    re.MULTILINE,
)


def run_python_script(script_path: str) -> str:
    """Runs a Python script at the given path and returns combined stdout/stderr.

    If the script fails, capture the error message in the returned text.
    """
    print(f"[DEBUG] Running script: {script_path}")
    try:
        result = subprocess.run(
            ["python", script_path],
            capture_output=True,
            text=True,
            check=False,  # Don't raise CalledProcessError if return code != 0
        )
        # Combine stdout and stderr
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
    except Exception as e:
        output = f"Error running {script_path}:\n{e}"
    return output


def create_logs_path(original_path: str) -> str:
    """Transforms a .py path into a logs path with .txt extension.

    Example: docs/path/src/foo.py => docs/path/logs/foo.txt
    """
    path_parts = original_path.split("/")
    # Replace 'src' with 'logs' if present, else insert 'logs' just before the filename
    if "src" in path_parts:
        idx = path_parts.index("src")
        path_parts[idx] = "logs"
    else:
        path_parts.insert(-1, "logs")
    # Convert the filename from .py to .txt
    path_parts[-1] = os.path.splitext(path_parts[-1])[0] + ".txt"
    return "/".join(path_parts)


def process_md_file(md_path: str) -> bool:
    """Process a single Markdown file sequentially.

    1) Find all spans of "Code/Logs" that are already done (DONE_BLOCK_PATTERN).
    2) Find code blocks referencing .py files (CODE_BLOCK_PATTERN).
    3) For each code block, if it's inside a done-block span, skip it.
    4) Otherwise:
       - Run the .py script
       - If output is non-empty (after stripping), create logs file + transform snippet
       - If empty, skip
    5) Return True if the file changed, otherwise False.
    """
    print(f"[DEBUG] Processing file: {md_path}")
    with open(md_path, encoding="utf-8") as f:
        original_content = f.read()

    #  We'll manually iterate over code-block matches with re.finditer
    #  so we can do custom logic for each match.
    changes = []
    last_pos = 0  # track where we've appended up to in the new content
    new_content_parts: list[str] = []

    for match in CODE_BLOCK_PATTERN.finditer(original_content):
        snippet_start, snippet_end = match.span()
        code_block_content = match.group(1)  # entire code block text
        py_file_path = match.group(2)  # the extracted "something.py"

        # First, append everything from the last position up to snippet_start
        new_content_parts.append(original_content[last_pos:snippet_start])

        # 3) Check if this snippet is inside a done block
        # Not in a done block, let's see if we can replace it
        print(f"[DEBUG] Found snippet referencing: {py_file_path}")

        # Run the .py script
        log_output = run_python_script(py_file_path)
        log_output = log_output.rstrip()  # strip trailing whitespace

        if not log_output:
            # 4) If empty, leave snippet unchanged
            print(f"[DEBUG] Script output empty. Skipping update for {py_file_path}.")
            new_content_parts.append(original_content[snippet_start:snippet_end])
        else:
            # 4) If non-empty, write logs and transform snippet into Code/Logs
            logs_path = create_logs_path(py_file_path)
            logs_dir = os.path.dirname(logs_path)
            if logs_dir and not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)

            print(f"[DEBUG] Writing log output to: {logs_path}")
            with open(logs_path, "w", encoding="utf-8") as logfile:
                logfile.write(log_output)

            # Build new Code/Logs block
            # Original snippet's code block content is included in "Code" tab
            new_block = (
                '=== "Code"\n'
                "    ```python\n"
                f"    {code_block_content}\n"
                "    ```\n\n"
                '=== "Logs"\n'
                "    ```python\n"
                f'    --8<-- "{logs_path}"\n'
                "    ```"
            )
            new_content_parts.append(new_block)
            print(f"[DEBUG] Replaced snippet for {py_file_path} with Code/Logs block.")
            changes.append(True)

        last_pos = snippet_end

    # Append any remaining text after the last match
    new_content_parts.append(original_content[last_pos:])

    # Join everything together
    new_content = "".join(new_content_parts)

    if new_content != original_content:
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"[INFO] Updated: {md_path}")
        return True

    return False


def update_markdown_files(root_dir: str) -> None:
    """Recursively find all .md files under root_dir.

    Process them in parallel (one file per thread). Each file's snippets are handled in sequence.
    """
    # Collect Markdown files
    md_files: list[str] = []
    for subdir, _, files in os.walk(root_dir):
        for filename in files:
            if filename.endswith(".md"):
                md_files.append(os.path.join(subdir, filename))

    if not md_files:
        print(f"[WARN] No Markdown files found in: {root_dir}")
        return

    updated_files = 0
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_file = {executor.submit(process_md_file, md_path): md_path for md_path in md_files}
        for future in concurrent.futures.as_completed(future_to_file):
            md_path = future_to_file[future]
            try:
                changed = future.result()
                if changed:
                    updated_files += 1
            except Exception as e:
                print(f"[ERROR] Exception processing {md_path}: {e}")

    print(f"[INFO] Processed {len(md_files)} Markdown files. Updated {updated_files} files.")


def main() -> None:
    """Entry point: accept a directory from sys.argv, defaulting to ./docs."""
    root_directory = sys.argv[1] if len(sys.argv) > 1 else "./docs"

    if not os.path.isdir(root_directory):
        print(f"[ERROR] {root_directory} is not a valid directory.")
        sys.exit(1)

    update_markdown_files(root_directory)


if __name__ == "__main__":
    main()
