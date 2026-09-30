from dataclasses import dataclass, field
from typing import Any

@dataclass
class Chunk:
    """
    A chunk produced from a source document
    """
    chunk_id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EnrichedChunk:
    """
    A chunk produced after enrichment
    """
    chunk_id: str
    document_id: str
    content: str
    title: str
    summary: str
    keywords: list[str] = field(default_factory=list)
    questions: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)