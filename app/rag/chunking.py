from dataclasses import dataclass, field
from typing import Any

import numpy as np

from .ingestion import Document
from .fixedTokenChunker import FixedTokenChunker
from .semanticChunker import SemanticChunker
