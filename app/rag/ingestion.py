from dataclasses import dataclass, field
from pathlib import Path
from datetime import date
from typing import Any
import re


DATE_FILENAME_PATTERN = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\.md$"
)


@dataclass
class Document:
    """
    Represents one source document before chunking.
    """

    document_id: str
    content: str
    source: str
    metadata: dict[str, Any] = field(default_factory=dict)


def load_markdown_documents(dataset_dir: str = "./dataset") -> list[Document]:
    """
    Load all Markdown diary entries from the dataset directory.

    Expected filename format:

        YYYY-MM-DD.md

    Example:

        2025-04-17.md
    """

    dataset_path = Path(dataset_dir)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {dataset_path}"
        )

    if not dataset_path.is_dir():
        raise NotADirectoryError(
            f"Dataset path is not a directory: {dataset_path}"
        )

    documents: list[Document] = []

    for file_path in sorted(dataset_path.glob("*.md")):
        match = DATE_FILENAME_PATTERN.match(file_path.name)

        if not match:
            print(
                f"Skipping {file_path.name}: "
                "filename does not match YYYY-MM-DD.md"
            )
            continue

        date_string = match.group("date")

        try:
            entry_date = date.fromisoformat(date_string)
        except ValueError:
            print(
                f"Skipping {file_path.name}: invalid date"
            )
            continue

        content = file_path.read_text(
            encoding="utf-8"
        ).strip()

        if not content:
            print(
                f"Skipping {file_path.name}: empty file"
            )
            continue

        document_id = file_path.stem

        documents.append(
            Document(
                document_id=document_id,
                content=content,
                source=str(file_path),
                metadata={
                    "filename": file_path.name,
                    "date": date_string,
                    "date_object": entry_date,
                    "file_type": "markdown",
                },
            )
        )

    return documents