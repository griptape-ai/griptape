from contextlib import contextmanager
from .base_loader import BaseLoader
from .text_loader import TextLoader
from .csv_loader import CsvLoader
from .file_loader import FileLoader

@contextmanager
def optional_dependencies(error: str = "ignore"):
    assert error in {"raise", "warn", "ignore"}
    try:
        yield None
    except ImportError as e:
        if error == "raise":
            raise e
        if error == "warn":
            msg = f'Missing optional dependency "{e.name}". Use pip or conda to install.'
            print(f'Warning: {msg}')


with optional_dependencies("warn"):
    from .sql_loader import SqlLoader
    from .pdf_loader import PdfLoader
    from .web_loader import WebLoader
    from .dataframe_loader import DataFrameLoader

__all__ = [
    "BaseLoader",
    "TextLoader",
    "PdfLoader",
    "WebLoader",
    "SqlLoader",
    "CsvLoader",
    "DataFrameLoader",
    "FileLoader"
]
