from typing import Generator

from ia.models import ChunkDocumeto


class Rag:
    @staticmethod
    def top_k_docs(query: str, k: int = 5) -> list[dict]:
        ChunkDocumeto

    @staticmethod
    def invoke(query: str) -> Generator[str, None, None]:
        ...
