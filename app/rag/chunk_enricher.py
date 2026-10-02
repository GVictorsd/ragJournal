import json
from typing import Dict, Any
from ollama import Client

class ChunkEnricher:
    def __init__(
        self,
        ollama_host: str,
        model: str = "qwen2.5:3b"
    ):
        self.client = Client(host=ollama_host)
        self.model = model

    def enrich_chunk(self, chunk):

        content = chunk["content"]

        topic = chunk.get(
            "metadata", {}
        ).get("topic", "")

        prompt = f"""
You are enriching a personal diary chunk for a
Retrieval-Augmented Generation (RAG) system.

Analyze ONLY the information contained in the chunk.

Topic:
{topic}

Chunk:
{content}

Generate:

1. title
   - A concise descriptive title.

2. summary
    - Summarize the main meaning.
    - 1-2 sentences.
    - Do not invent information.

3. keywords
    - Generate 5-10 important keywords or short phrases.
    - Focus on concepts, activities, goals, technologies,
        decisions and important subjects.
    - Avoid generic words.

4. questions
    - Generate 3-5 questions that this chunk can answer.
    - Questions should resemble realistic user queries.
    - Questions should be useful for semantic retrieval.
    - Do not ask questions whose answers are not contained
        in the chunk.

Do not invent information.

Return ONLY JSON in this format:

{{
    "title": "string",
    "summary": "string",
    "keywords": [
        "keyword 1",
        "keyword 2"
    ],
    "questions": [
        "question 1",
        "question 2"
    ]
}}
"""

        response = self.client.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            format="json"
        )

        return json.loads(
            response["message"]["content"]
        )