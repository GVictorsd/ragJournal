import sys
from pathlib import Path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from app.models.chunk import Chunk

import numpy as np
import spacy

from sentence_transformers import SentenceTransformer

# from .ingestion import Document, Chunk
from .ingestion import Document


class SemanticChunker:
    """
    Sentence-based semantic chunker.

    Pipeline:

        Document
            ↓
        spaCy sentence splitting
            ↓
        Sentence embeddings
            ↓
        Compare adjacent sentences
            ↓
        Group semantically similar sentences
            ↓
        Create semantic chunks
    """

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        similarity_threshold: float = 0.65,
        min_sentences: int = 2,
        max_sentences: int = 8,
        max_chunk_characters: int = 4000,
    ):
        if min_sentences <= 0:
            raise ValueError(
                "min_sentences must be greater than 0"
            )

        if max_sentences < min_sentences:
            raise ValueError(
                "max_sentences must be >= min_sentences"
            )

        if not 0.0 <= similarity_threshold <= 1.0:
            raise ValueError(
                "similarity_threshold must be between 0 and 1"
            )

        if max_chunk_characters <= 0:
            raise ValueError(
                "max_chunk_characters must be greater than 0"
            )

        # spaCy is used only for sentence segmentation.
        self.nlp = spacy.load(
            "en_core_web_sm",
            disable=[
                "ner",
                "parser",
                "lemmatizer",
                "textcat",
            ],
        )

        # Add the lightweight sentencizer because the parser has been disabled.
        if "sentencizer" not in self.nlp.pipe_names:
            self.nlp.add_pipe("sentencizer")

        # Sentence embedding model.
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = (similarity_threshold)
        self.min_sentences = min_sentences
        self.max_sentences = max_sentences
        self.max_chunk_characters = (max_chunk_characters)

    def split_into_sentences(
        self,
        text: str,
    ) -> list[str]:
        """
        Split document text into sentences using spaCy.
        """

        doc = self.nlp(text)

        sentences = [
            sentence.text.strip()
            for sentence in doc.sents
            if sentence.text.strip()
        ]

        return sentences

    @staticmethod
    def cosine_similarity(
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        """

        denominator = (
            np.linalg.norm(a)
            * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )

    def chunk_document(
        self,
        document: Document,
    ) -> list[Chunk]:
        """
        Split a single document into semantic chunks.
        """

        sentences = self.split_into_sentences(
            document.content
        )

        if not sentences:
            return []

        # Generate one embedding per sentence.
        embeddings = self.model.encode(
            sentences,
            normalize_embeddings=True,
            show_progress_bar=False,
        )

        chunks: list[Chunk] = []

        current_sentences: list[str] = []
        current_sentence_indices: list[int] = []

        chunk_index = 0

        def flush_chunk():
            nonlocal chunk_index

            if not current_sentences:
                return

            content = " ".join(
                current_sentences
            ).strip()

            chunks.append(
                Chunk(
                    chunk_id=(
                        f"{document.document_id}"
                        f"_chunk_{chunk_index}"
                    ),
                    document_id=document.document_id,
                    content=content,
                    metadata={
                        **document.metadata,
                        "chunk_index": chunk_index,
                        "chunking_method": "semantic",
                        "sentence_start": (
                            current_sentence_indices[0]
                        ),
                        "sentence_end": (
                            current_sentence_indices[-1]
                        ),
                        "sentence_count": len(
                            current_sentences
                        ),
                    },
                )
            )

            chunk_index += 1

        for i, sentence in enumerate(sentences):

            # First sentence always starts the current chunk.
            if not current_sentences:

                current_sentences.append(
                    sentence
                )

                current_sentence_indices.append(
                    i
                )

                continue

            previous_embedding = embeddings[i - 1]
            current_embedding = embeddings[i]

            similarity = self.cosine_similarity(
                previous_embedding,
                current_embedding,
            )

            candidate_sentences = (
                current_sentences + [sentence]
            )

            candidate_content = " ".join(
                candidate_sentences
            )

            sentence_count = len(
                candidate_sentences
            )

            exceeds_max_sentences = (
                sentence_count > self.max_sentences
            )

            exceeds_max_characters = (
                len(candidate_content)
                > self.max_chunk_characters
            )

            semantic_break = (
                similarity
                < self.similarity_threshold
            )

            # Only allow a semantic split if the current
            # chunk has reached the minimum size.
            should_split = (
                len(current_sentences)
                >= self.min_sentences
                and (
                    semantic_break
                    or exceeds_max_sentences
                    or exceeds_max_characters
                )
            )

            if should_split:

                flush_chunk()

                current_sentences.clear()
                current_sentence_indices.clear()

                current_sentences.append(
                    sentence
                )

                current_sentence_indices.append(
                    i
                )

            else:

                current_sentences.append(
                    sentence
                )

                current_sentence_indices.append(
                    i
                )

        # Flush final chunk.
        flush_chunk()

        return chunks

    def chunk_documents(
        self,
        documents: list[Document],
    ) -> list[Chunk]:
        """
        Chunk multiple documents.
        """

        chunks: list[Chunk] = []

        for document in documents:

            document_chunks = (
                self.chunk_document(document)
            )

            chunks.extend(
                document_chunks
            )

        return chunks

