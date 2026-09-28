from dataclasses import dataclass, field
from pathlib import Path
from datetime import date
from typing import Any
import re


# DATE_FILENAME_PATTERN = re.compile(
#     r"^(?P<date>\d{4}-\d{2}-\d{2})\.md$"
# )
DATE_FILENAME_PATTERN = re.compile(
    r"^\d+_(?P<date>\d{4}-\d{2}-\d{2})_.+\.md$"
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
    dataset_path = Path(dataset_dir).resolve()

    # dataset_path = Path(dataset_dir)

    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset directory does not exist: {dataset_path}"
        )

    if not dataset_path.is_dir():
        raise NotADirectoryError(
            f"Dataset path is not a directory: {dataset_path}"
        )

    documents: list[Document] = []

    # TODO: remove count later
    count = 0
    max_count = 5
    for file_path in sorted(dataset_path.glob("*.md")):
        # TODO: remove later
        count += 1
        if count > max_count:
            break


        document = parse_markdown_file(file_path)

        if document is None:
            continue

        documents.append(document)


    #     match = DATE_FILENAME_PATTERN.match(file_path.name)

    #     if not match:
    #         print(
    #             f"Skipping {file_path.name}: "
    #             "filename does not match YYYY-MM-DD.md"
    #         )
    #         continue

    #     date_string = match.group("date")

    #     try:
    #         entry_date = date.fromisoformat(date_string)
    #     except ValueError:
    #         print(
    #             f"Skipping {file_path.name}: invalid date"
    #         )
    #         continue

    #     content = file_path.read_text(
    #         encoding="utf-8"
    #     ).strip()

    #     if not content:
    #         print(
    #             f"Skipping {file_path.name}: empty file"
    #         )
    #         continue

    #     document_id = file_path.stem

    #     documents.append(
    #         Document(
    #             document_id=document_id,
    #             content=content,
    #             source=str(file_path),
    #             metadata={
    #                 "filename": file_path.name,
    #                 "date": date_string,
    #                 "date_object": entry_date,
    #                 "file_type": "markdown",
    #             },
    #         )
    #     )

    return documents





import re
from datetime import date
from pathlib import Path
import yaml


TITLE_PATTERN = re.compile(
    r"^#\s+(.+?)\s*$",
    re.MULTILINE
)


def parse_markdown_file(file_path: Path):
    """
    Parse a journal Markdown file into:
        - front matter metadata
        - title
        - journal content
    """

    raw_text = file_path.read_text(encoding="utf-8").strip()

    if not raw_text:
        return None

    # ---------------------------------------------------------
    # 1. Extract YAML front matter
    # ---------------------------------------------------------
    front_matter = {}

    front_matter_match = re.match(
        r"^---\s*\n(.*?)\n---\s*\n?",
        raw_text,
        re.DOTALL
    )

    if front_matter_match:
        yaml_text = front_matter_match.group(1)

        try:
            front_matter = yaml.safe_load(yaml_text) or {}
        except yaml.YAMLError as exc:
            print(
                f"Skipping {file_path.name}: "
                f"invalid YAML front matter: {exc}"
            )
            return None

        remaining_content = raw_text[
            front_matter_match.end():
        ].strip()

    else:
        print(
            f"Warning: {file_path.name} has no YAML front matter"
        )
        remaining_content = raw_text

    # ---------------------------------------------------------
    # 2. Extract title
    # ---------------------------------------------------------
    title_match = TITLE_PATTERN.search(remaining_content)

    if title_match:
        title = title_match.group(1).strip()

        # Remove the title from the remaining content
        content = (
            remaining_content[:title_match.start()]
            + remaining_content[title_match.end():]
        ).strip()

    else:
        title = file_path.stem
        content = remaining_content.strip()

    # ---------------------------------------------------------
    # 3. Remove RAG Metadata section from content
    # ---------------------------------------------------------
    rag_metadata_pattern = re.compile(
        r"\n##\s+RAG Metadata\s*\n.*$",
        re.IGNORECASE | re.DOTALL
    )

    content = rag_metadata_pattern.sub(
        "",
        content
    ).strip()

    # ---------------------------------------------------------
    # 4. Normalize metadata
    # ---------------------------------------------------------
    date_string = front_matter.get("date")

    if date_string:
        date_string = str(date_string)

        try:
            entry_date = date.fromisoformat(date_string)
        except ValueError:
            print(
                f"Skipping {file_path.name}: "
                f"invalid date '{date_string}'"
            )
            return None
    else:
        entry_date = None

    # ---------------------------------------------------------
    # 5. Build metadata
    # ---------------------------------------------------------
    metadata = {
        # YAML front matter
        **front_matter,

        # File-level information
        "filename": file_path.name,
        "file_type": "markdown",
        "source": str(file_path),

        # Parsed title
        "title": title,
    }

    # Keep the Python date object if useful for filtering
    if entry_date:
        metadata["date_object"] = entry_date

    # ---------------------------------------------------------
    # 6. Validate content
    # ---------------------------------------------------------
    if not content:
        print(
            f"Skipping {file_path.name}: "
            "empty journal content"
        )
        return None

    # ---------------------------------------------------------
    # 7. Create Haystack Document
    # ---------------------------------------------------------
    document_id = front_matter.get(
        "entry_id",
        file_path.stem
    )

    return Document(
        document_id=document_id,
        source=str(file_path),
        content=content,
        metadata=metadata,
    )