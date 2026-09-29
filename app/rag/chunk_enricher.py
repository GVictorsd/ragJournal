import json
from typing import Dict, Any

import ollama
from ollama import Client


# class ChunkEnricher:

#     def __init__(
#         self,
#         model: str = "qwen2.5:3b"
#     ):
#         self.model = model

#     def _build_prompt(
#         self,
#         chunk: Dict[str, Any]
#     ) -> str:

#         content = chunk["content"]

#         metadata = chunk.get("metadata", {})

#         topic = metadata.get("topic", "")
#         date = metadata.get("date", "")

#         return f"""
#             You are enriching a personal diary chunk for a
#             Retrieval-Augmented Generation (RAG) system.

#             Analyze ONLY the information contained in the chunk.

#             Topic: {topic}
#             Date: {date}

#             CHUNK:
#             ---
#             {content}
#             ---

#             Generate:

#             1. title
#             - A concise descriptive title.
#             - 5-10 words.
#             - Do not simply copy the topic.

#             2. summary
#             - Summarize the main meaning.
#             - 1-2 sentences.
#             - Do not invent information.

#             3. keywords
#             - Generate 5-10 important keywords or short phrases.
#             - Focus on concepts, activities, goals, technologies,
#                 decisions and important subjects.
#             - Avoid generic words.

#             4. questions
#             - Generate 3-5 questions that this chunk can answer.
#             - Questions should resemble realistic user queries.
#             - Questions should be useful for semantic retrieval.
#             - Do not ask questions whose answers are not contained
#                 in the chunk.

#             Return ONLY valid JSON.

#             Use exactly this structure:

#             {{
#                 "title": "string",
#                 "summary": "string",
#                 "keywords": [
#                     "keyword 1",
#                     "keyword 2"
#                 ],
#                 "questions": [
#                     "question 1",
#                     "question 2"
#                 ]
#             }}
#         """

#     def enrich_chunk(
#         self,
#         chunk: Dict[str, Any]
#     ) -> Dict[str, Any]:

#         prompt = self._build_prompt(chunk)

#         response = ollama.chat(
#             model=self.model,
#             messages=[
#                 {
#                     "role": "user",
#                     "content": prompt
#                 }
#             ],
#             format="json",
#             options={
#                 "temperature": 0.2
#             }
#         )

#         result = response["message"]["content"]

#         enrichment = json.loads(result)

#         self._validate(enrichment)

#         return enrichment

#     @staticmethod
#     def _validate(
#         enrichment: Dict[str, Any]
#     ):

#         required = [
#             "title",
#             "summary",
#             "keywords",
#             "questions"
#         ]

#         for field in required:
#             if field not in enrichment:
#                 raise ValueError(
#                     f"Missing field: {field}"
#                 )

#         if not isinstance(
#             enrichment["keywords"],
#             list
#         ):
#             raise ValueError(
#                 "keywords must be a list"
#             )

#         if not isinstance(
#             enrichment["questions"],
#             list
#         ):
#             raise ValueError(
#                 "questions must be a list"
#             )




class ChunkEnricher:

    def __init__(
        self,
        ollama_host: str,
        model: str = "qwen2.5:3b"
    ):
        self.client = Client(
            host=ollama_host
        )

        self.model = model

    def enrich_chunk(self, chunk):

        content = chunk["content"]

        topic = chunk.get(
            "metadata", {}
        ).get("topic", "")

        prompt = f"""
Analyze the following personal diary chunk.

Topic:
{topic}

Chunk:
{content}

Generate:

1. title
   A concise descriptive title.

2. summary
   A 1-2 sentence summary.

3. keywords
   5-10 important keywords or short phrases.

4. questions
   3-5 questions that this chunk can answer.

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