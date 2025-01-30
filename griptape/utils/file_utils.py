from __future__ import annotations

import mimetypes

import filetype


def get_mime_type(file_path_or_bytes: str | bytes) -> str:
    filetype_guess = filetype.guess(file_path_or_bytes)

    if filetype_guess is None:
        if isinstance(file_path_or_bytes, bytes):
            return "application/octet-stream"
        type_, _ = mimetypes.guess_type(file_path_or_bytes)
        if type_ is None:
            return "application/octet-stream"
        else:
            return type_
    else:
        return filetype_guess.mime
