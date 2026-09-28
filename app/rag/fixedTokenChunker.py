import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.models.chunk import Chunk

import tiktoken

class FixedTokenChunker:
    """
    Splits documents into fixed-size token chunks with overlap.

    Example:

        chunk_size = 500
        overlap = 100

    Chunk 1:
        tokens 0 - 499

    Chunk 2:
        tokens 400 - 899

    Chunk 3:
        tokens 800 - 1299
    """

    def __init__(
        self,
        chunk_size: int = 500,
        overlap: int = 100,
        encoding_name: str = "cl100k_base",
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than zero"
            )

        if overlap < 0:
            raise ValueError(
                "overlap cannot be negative"
            )

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

        self.encoding = tiktoken.get_encoding(
            encoding_name
        )

    def chunk_document(
        self,
        document: Document,
    ) -> list[Chunk]:

        tokens = self.encoding.encode(
            document.content
        )

        chunks: list[Chunk] = []

        step = self.chunk_size - self.overlap

        start = 0
        chunk_index = 0

        while start < len(tokens):

            end = min(
                start + self.chunk_size,
                len(tokens),
            )

            chunk_tokens = tokens[start:end]

            chunk_text = self.encoding.decode(
                chunk_tokens
            ).strip()

            if chunk_text:

                chunks.append(
                    Chunk(
                        chunk_id=(
                            f"{document.document_id}"
                            f"_chunk_{chunk_index}"
                        ),
                        document_id=document.document_id,
                        content=chunk_text,
                        metadata={
                            **document.metadata,
                            "chunk_index": chunk_index,
                            "chunking_method": "fixed_token",
                            "start_token": start,
                            "end_token": end,
                            "token_count": len(chunk_tokens),
                        },
                    )
                )

            chunk_index += 1
            start += step

        return chunks

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:

        chunks: list[Chunk] = []

        for document in documents:
            chunks.extend(
                self.chunk_document(document)
            )

        return chunks