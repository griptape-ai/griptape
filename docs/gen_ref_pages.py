"""Generate the code reference pages and navigation."""

from pathlib import Path
from textwrap import dedent

import mkdocs_gen_files


def build_reference_docs() -> None:
    nav = mkdocs_gen_files.Nav()

    for path in sorted(Path("griptape").rglob("*.py")):
        module_path = path.relative_to(".").with_suffix("")
        doc_path = path.relative_to(".").with_suffix(".md")
        full_doc_path = Path("reference", doc_path)

        parts = tuple(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            ident = ".".join(parts)
            fd.write(f"::: {ident}")

        mkdocs_gen_files.set_edit_path(full_doc_path, Path("..") / path)

    with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(["---\n", "search:\n", "\x20\x20exclude: true\n", "---\n"])
        nav_file.writelines(nav.build_literate_nav())
    with mkdocs_gen_files.open("reference/griptape/index.md", "w") as index_file:
        index_file.write(
            dedent(
                """
        # Overview
        This section of the documentation is dedicated to a reference API of Griptape.
        Here you will find every class, function, and method that is available to you when using the library.
        """
            )
        )


build_reference_docs()
