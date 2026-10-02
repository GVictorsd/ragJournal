# Journal RAG

A **Retrieval-Augmented Generation (RAG) application** for querying a collection of personal journal entries using semantic search, metadata filtering, reranking, and LLM-based answer generation.

The project is designed as a practical exploration of modern RAG pipelines — from document ingestion and chunking to embeddings, vector search, retrieval evaluation, reranking, generation, and source attribution.

---

## ✨ Features

* **Journal document ingestion**
* **Multiple chunking strategies**
  * Fixed-size token-based chunking with overlap
  * Sentence-based semantic chunking
* **Text preprocessing and enrichment**
  * Title and summary generation
  * Keywords
  * Question generation
* **Text embeddings** for semantic retrieval
* **ChromaDB** vector database
* **Semantic similarity search**
* **Metadata filtering**
* **Reranking** using a cross-encoder
* **LLM-based answer generation**
* **Source attribution** for generated answers
* Retrieval evaluation
* Comparison of different embedding and retrieval strategies

---

## Architecture

The project follows a typical RAG pipeline:

```text
                 ┌──────────────────────┐
                 │   Journal Markdown   │
                 │       Dataset        │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Document Ingestion   │
                 │ & Parsing            │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Chunking             │
                 │ • Fixed-size tokens  │
                 │ • Semantic chunking  │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Chunk Enrichment     │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Embedding Generation │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │      ChromaDB        │
                 │ Vector + Metadata    │
                 └──────────┬───────────┘
                            │
                     User Query
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Semantic Search +    │
                 │ Metadata Filtering   │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │     Reranking        │
                 │  Cross-Encoder       │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │    LLM Generation    │
                 │   Context + Query    │
                 └──────────┬───────────┘
                            ▼
                 ┌──────────────────────┐
                 │ Answer + Source      │
                 │ attribution          │
                 └──────────────────────┘
```

---

## Repository Structure

```text
ragJournal/
│
├── app/
│   └── ...                  # RAG application / Helper methods
│
├── chroma_db/
│   └── ...                  # Local ChromaDB persistent storage
│
├── data/
│   └── ...                  # Intermediate and processed data
│
├── dataset/
│   └── ...                  # Source journal entries
│
├── scripts/
│   └── ...                  # Data processing, embedding and evaluation scripts
│
├── requirements.txt         # Python dependencies
│
└── README.md
```

### `dataset/`

Contains the original journal entries used as the source documents.
The entries are stored as Markdown files and contain multiple topics such as:

### `data/`

Contains intermediate artifacts generated throughout the RAG pipeline.
These include the chunks, enriched chunks and embeddings
These artifacts make it possible to inspect and compare each stage of the pipeline independently.

### `chroma_db/`

Persistent local storage for the ChromaDB vector database.

The database stores:
* Chunk IDs
* Embeddings
* Original/enriched text
* Document IDs
* Dates
* Topics
* Other metadata

Metadata can be used alongside semantic search for filtered retrieval.

### `scripts/`

Contains standalone scripts for different stages of the pipeline.

Typical responsibilities include:

```text
scripts/
├── ingestion
├── chunking
├── enrichment
├── embedding generation
├── chroma loading
├── retrieval
├── reranking
└── evaluation
```

Keeping these operations as separate scripts makes it easier to experiment with individual RAG components.

---

# Getting Started

## 1. Create a virtual environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
```

---

# RAG Pipeline

## 1. Document Ingestion

The source Markdown journal files are loaded and parsed into structured documents.
Each document contains information such as:

```text
Document
├── document_id
├── date
├── title
├── topic
└── content
```

---

## 2. Chunking

Two chunking approaches are explored.

### Fixed-size chunking with overlap

Documents are split into fixed length chunks based on a target token size with overlapping tokens.
The overlap helps preserve context across chunk boundaries.

### Semantic chunking

This approach uses embeddings to group semantically similar sentences across a document to create chunks.
Semantic chunking can produce easily understandable chunks that closely align to the content's subjects.

---

## 3. Chunk Enrichment

Chunks are enriched with additional information before embedding.
This involves augmenting chunks with additional data like summary, keywords and questions

Example:

```json
{
  "chunk_id": "journal-001_chunk_0",
  "document_id": "journal-001",
  "content": "...",
  "title": "Year-Long Career Goals",
  "summary": "...",
  "keywords": [
    "career",
    "software engineering",
    "learning"
  ],
  "questions": [
    "What are the author's career goals?",
    "What skills does the author want to improve?"
  ],
  "metadata": {
    "date": "2026-01-03",
    "topic": "Career Planning"
  }
}
```

Enrichment provides additional semantic signals that can be used during retrieval and experimentation.

---

# Embeddings

Each chunk is converted into a vector representation using an embedding model.
The embeddings are stored in a vector database(ChromaDB) along with the metadata for Semantic retrieval and Metadata filtering.
Different embedding models can be evaluated against the same dataset to compare retrieval quality.

---

# Retrieval

The initial retrieval stage performs semantic similarity search against ChromaDB.

The query is converted into an embedding and compared against stored chunk embeddings.

The initial retrieval might return:

```text
Top 10 candidate chunks
        ↓
   Reranking
        ↓
Top 3–5 relevant chunks
```

Metadata filtering can also be applied when appropriate.

For example:

```text
topic = "Career Planning"
date >= "2026-01-01"
```

This allows semantic retrieval and structured filtering to work together.

---

# Reranking

Vector similarity provides an efficient first-stage retrieval mechanism, but the highest similarity results are not always the most relevant.

The project therefore uses a **two-stage retrieval strategy**:

```text
                    User Query
                        │
                        ▼
              ┌─────────────────┐
              │ Vector Retrieval│
              │    Top-K        │
              └────────┬────────┘
                       │
                  Candidate Chunks
                       │
                       ▼
              ┌─────────────────┐
              │  Cross-Encoder  │
              │    Reranker     │
              └────────┬────────┘
                       │
                       ▼
                 Final Top-N
```

The cross-encoder evaluates the query and candidate chunk together, allowing a more detailed relevance score.

---

# LLM Generation

The final retrieved chunks are provided to an LLM as context.

Conceptually:
User Query + Retrieved Context -> LLM -> Grounded Answer

The generation step is instructed to use the retrieved journal entries rather than relying solely on the model's internal knowledge.

---

# Source Attribution

Generated answers include references to the journal chunks used to construct the response.

For example:

```text
Answer:

You wanted to become a better chef by
deepening your understanding of traditional dishes and local ingredients

Sources:
- journal-001_chunk_0
- journal-014_chunk_2
```

Source attribution makes the generated response more transparent and helps verify whether the answer is actually supported by the retrieved context.

---

# Retrieval Evaluation

Evaluation of the retrieval pipeline.

Possible metrics include:

### Recall@K

Measures whether the relevant chunk appears within the top K results.

```text
Recall@5 =
relevant queries retrieved in top 5
------------------------------------
       total relevant queries
```

### Precision@K

Measures how many of the retrieved results are relevant.

```text
Precision@5 =
relevant results in top 5
-------------------------
          5
```

### MRR

**Mean Reciprocal Rank** evaluates how high the first relevant result appears.

### NDCG

**Normalized Discounted Cumulative Gain** considers both relevance and ranking position.

The evaluation dataset can contain:

```json
{
  "query": "What are my career goals?",
  "relevant_chunks": [
    "journal-001_chunk_0",
    "journal-012_chunk_1"
  ]
}
```

This makes it possible to quantitatively compare:

* Chunking strategies
* Embedding models
* Retrieval parameters
* Reranking
* Metadata filtering

---

# Experiments

The repository is intended to be an experimentation platform for understanding RAG rather than a single fixed implementation.

Some of the experiments include:

| Component     | Experiments                           |
| ------------- | ------------------------------------- |
| Chunking      | Fixed-size vs sentence-based          |
| Chunk overlap | Different overlap sizes               |
| Embeddings    | Multiple embedding models             |
| Retrieval     | Different Top-K values                |
| Filtering     | Semantic + metadata filtering         |
| Reranking     | Vector similarity vs cross-encoder    |
| Context       | Different numbers of retrieved chunks |
| Generation    | Different prompting strategies        |
| Evaluation    | Recall@K, Precision@K, MRR, NDCG      |

---

# 🛠️ Technology Stack

* **Python**
* **ChromaDB** — vector database
* **Sentence Transformers / Cross-Encoders** — embeddings and reranking
* **spaCy** — sentence processing
* **LLM API** — answer generation
* **Markdown** — source journal format

---

# 🎯 Learning Objectives

This project was built to understand the complete lifecycle of a production-style RAG system:

1. Document ingestion
2. Document parsing
3. Chunking
4. Text preprocessing
5. Chunk enrichment
6. Embedding generation
7. Vector database storage
8. Semantic retrieval
9. Metadata filtering
10. Retrieval evaluation
11. Reranking
12. Context construction
13. LLM generation
14. Source attribution

Rather than treating RAG as simply:

```text
Documents → Embeddings → LLM
```

the project explores RAG as a complete retrieval and information-processing pipeline.

---