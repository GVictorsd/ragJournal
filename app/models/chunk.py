from dataclasses import dataclass, field
from typing import Any

@dataclass
class Chunk:
    """
    A chunk produced from a source document.
    """

    chunk_id: str
    document_id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)