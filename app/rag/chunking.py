from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .ingestion import Document
from .fixedTokenChunker import FixedTokenChunker
from .semanticChunker import SemanticChunker


@dataclass
class Chunk:
    """
    A chunk produced from a source document.
    """

    chunk_id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
