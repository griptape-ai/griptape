import mimetypes

import filetype


def get_mime_type(file_path: str) -> str:
    filetype_guess = filetype.guess(file_path)

    if filetype_guess is None:
        type_, _ = mimetypes.guess_type(file_path)
        if type_ is None:
            return "application/octet-stream"
        else:
            return type_
    else:
        return filetype_guess.mime
