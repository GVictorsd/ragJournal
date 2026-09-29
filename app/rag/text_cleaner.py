# NOT Used rn
import re
import unicodedata
from enum import Enum
from typing import Optional

# from spellchecker import SpellChecker
from spacy.lang.en.stop_words import STOP_WORDS
# from unidecode import unidecode


class LowercaseStrategy(str, Enum):
    NONE = "none"
    ALL = "all"
    WORDS_ONLY = "words_only"


class TextCleaner:
    """
    Cleans journal chunks before enrichment.

    Operations:
        1. Markdown/frontmatter removal
        2. Unicode normalization/removal
        3. Lowercasing
        4. Spelling correction
        5. Stop-word removal
    """

    def __init__(
        self,
        lowercase_strategy: LowercaseStrategy = LowercaseStrategy.ALL,
        remove_stopwords: bool = True,
        correct_spelling: bool = True,
        remove_unicode: bool = True,
    ):
        self.lowercase_strategy = lowercase_strategy
        self.remove_stopwords = remove_stopwords
        self.correct_spelling = correct_spelling
        self.remove_unicode = remove_unicode

        self.spell_checker = SpellChecker()

    # ---------------------------------------------------------
    # Public API
    # ---------------------------------------------------------

    def clean(self, text: str) -> str:
        """
        Run the complete cleaning pipeline.
        """

        text = self._remove_frontmatter(text)
        text = self._remove_markdown(text)

        if self.remove_unicode:
            text = self._remove_unicode(text)

        text = self._normalize_whitespace(text)

        if self.lowercase_strategy != LowercaseStrategy.NONE:
            text = self._lowercase(text)

        if self.correct_spelling:
            text = self._correct_spelling(text)

        if self.remove_stopwords:
            text = self._remove_stopwords(text)

        text = self._normalize_whitespace(text)

        return text.strip()

    # ---------------------------------------------------------
    # Markdown
    # ---------------------------------------------------------

    def _remove_frontmatter(self, text: str) -> str:
        """
        Remove YAML frontmatter:

        ---
        date: ...
        topic: ...
        ---
        """

        pattern = r"^\s*---\s*\n.*?\n---\s*\n"

        return re.sub(
            pattern,
            "",
            text,
            flags=re.DOTALL,
        )

    def _remove_markdown(self, text: str) -> str:
        """
        Convert common Markdown constructs into plain text.
        """

        # Headings
        text = re.sub(r"^#{1,6}\s*", "", text, flags=re.MULTILINE)

        # Bold / italic
        text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
        text = re.sub(r"__(.*?)__", r"\1", text)

        text = re.sub(r"\*(.*?)\*", r"\1", text)
        text = re.sub(r"_(.*?)_", r"\1", text)

        # Inline code
        text = re.sub(r"`([^`]*)`", r"\1", text)

        # Links
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)

        # Images
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)

        # Markdown bullets
        text = re.sub(r"^\s*[-*+]\s+", "", text, flags=re.MULTILINE)

        # Numbered lists
        text = re.sub(r"^\s*\d+\.\s+", "", text, flags=re.MULTILINE)

        return text

    # ---------------------------------------------------------
    # Unicode
    # ---------------------------------------------------------

    def _remove_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters to ASCII equivalents.

        Examples:

            café      -> cafe
            résumé    -> resume
            naïve     -> naive
            —         -> -
            “hello”   -> "hello"
        """

        # NFKD decomposition
        text = unicodedata.normalize("NFKD", text)

        # Convert Unicode -> ASCII
        text = unidecode(text)

        # Remove remaining non-ASCII characters
        text = text.encode(
            "ascii",
            errors="ignore",
        ).decode("ascii")

        return text

    # ---------------------------------------------------------
    # Lowercasing
    # ---------------------------------------------------------

    def _lowercase(self, text: str) -> str:

        if self.lowercase_strategy == LowercaseStrategy.ALL:
            return text.lower()

        if self.lowercase_strategy == LowercaseStrategy.WORDS_ONLY:
            return re.sub(
                r"\b[A-Za-z]+\b",
                lambda match: match.group(0).lower(),
                text,
            )

        return text

    # ---------------------------------------------------------
    # Spelling
    # ---------------------------------------------------------

    def _correct_spelling(self, text: str) -> str:
        """
        Correct obvious English spelling errors.

        Important:
        Avoid correcting words that contain digits or
        punctuation-heavy identifiers.
        """

        words = text.split()

        corrected_words = []

        for word in words:

            # Separate punctuation from word
            prefix_match = re.match(r"^[^\w]*", word)
            suffix_match = re.search(r"[^\w]*$", word)

            prefix = prefix_match.group(0) if prefix_match else ""
            suffix = suffix_match.group(0) if suffix_match else ""

            core = word[len(prefix):]

            if suffix:
                core = core[:-len(suffix)]

            # Don't modify numbers, URLs, IDs, etc.
            if (
                not core
                or any(char.isdigit() for char in core)
                or len(core) <= 2
                or not core.isalpha()
            ):
                corrected_words.append(word)
                continue

            corrected = self.spell_checker.correction(core)

            if corrected is None:
                corrected = core

            corrected_words.append(
                prefix + corrected + suffix
            )

        return " ".join(corrected_words)

    # ---------------------------------------------------------
    # Stop words
    # ---------------------------------------------------------

    def _remove_stopwords(self, text: str) -> str:

        words = text.split()

        filtered_words = []

        for word in words:

            # Remove punctuation when checking stopword
            normalized_word = re.sub(
                r"[^a-zA-Z]",
                "",
                word,
            ).lower()

            if normalized_word in STOP_WORDS:
                continue

            filtered_words.append(word)

        return " ".join(filtered_words)

    # ---------------------------------------------------------
    # Whitespace
    # ---------------------------------------------------------

    def _normalize_whitespace(self, text: str) -> str:

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()