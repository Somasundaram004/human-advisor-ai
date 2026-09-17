import json
import re
from pathlib import Path


class LocalKnowledgeBase:
    """Small reviewable local dataset with deterministic lexical retrieval."""

    def __init__(self, path: str = "data/knowledge.json"):
        self.path = Path(path)
        self.entries = json.loads(self.path.read_text(encoding="utf-8")) if self.path.exists() else []

    def search(self, question: str, limit: int = 3) -> list[dict]:
        tokens = self._tokens(question)
        ranked = []
        for entry in self.entries:
            haystack = self._tokens(" ".join([entry.get("topic", ""), *entry.get("questions", []), entry.get("answer", "")]))
            score = len(tokens & haystack)
            if score:
                ranked.append((score, entry))
        ranked.sort(key=lambda item: item[0], reverse=True)
        return [entry for _, entry in ranked[:limit]]

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9]+", text.casefold()) if len(token) > 2}