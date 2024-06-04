import io
import os

import pytest
from tests.utils.code_blocks import get_all_code_blocks, check_py_string


if "DOCS_ALL_CHANGED_FILES" in os.environ and os.environ["DOCS_ALL_CHANGED_FILES"] != "":
    docs_all_changed_files = os.environ["DOCS_ALL_CHANGED_FILES"].split()

    all_code_blocks = [get_all_code_blocks(changed_file) for changed_file in docs_all_changed_files]
    all_code_blocks = [block for sublist in all_code_blocks for block in sublist]
else:
    all_code_blocks = get_all_code_blocks("docs/**/*.md")


@pytest.mark.parametrize("block", all_code_blocks, ids=[f["id"] for f in all_code_blocks])
def test_code_block(block, monkeypatch):
    # Send some stdin for tests that use the Chat util
    monkeypatch.setattr("sys.stdin", io.StringIO("Hi\nexit\n"))

    check_py_string(block["code"])
