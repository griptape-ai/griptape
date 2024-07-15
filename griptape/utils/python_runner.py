from __future__ import annotations

import importlib
import sys
from io import StringIO

from attrs import define, field


@define
class PythonRunner:
    libs: dict[str, str] = field(factory=dict, kw_only=True)

    def run(self, code: str) -> str:
        global_stdout = sys.stdout
        sys.stdout = local_stdout = StringIO()

        try:
            for lib, alias in self.libs.items():
                imported_lib = importlib.import_module(lib)
                globals()[alias] = imported_lib

            exec(f"print({code})", {}, {alias: eval(alias) for alias in self.libs.values()})

            output = local_stdout.getvalue()
        except Exception as e:
            output = str(e)
        finally:
            sys.stdout = global_stdout

        return output.strip()
