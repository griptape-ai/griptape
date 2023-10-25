from griptape.chunkers import BaseChunker, ChunkSeparator


class MarkdownChunker(BaseChunker):
    DEFAULT_SEPARATORS = [
        ChunkSeparator("##", is_prefix=True),
        ChunkSeparator("###", is_prefix=True),
        ChunkSeparator("####", is_prefix=True),
        ChunkSeparator("#####", is_prefix=True),
        ChunkSeparator("######", is_prefix=True),
        ChunkSeparator("\n\n"),
        ChunkSeparator(". "),
        ChunkSeparator("! "),
        ChunkSeparator("? "),
        ChunkSeparator(" "),
    ]
