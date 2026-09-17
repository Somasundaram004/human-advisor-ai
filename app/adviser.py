import os
import urllib.request
import json

from .store import MemoryStore


class Adviser:
    def __init__(self, store: MemoryStore):
        self.store = store

    def answer(self, question: str, context: dict) -> dict:
        memories = self.store.recall(question, limit=8)
        prompt = json.dumps({"question": question, "context": context, "memories": memories})
        answer = self._llm(prompt)
        return {
            "answer": answer or "I need human guidance before recommending an action. Review the recalled context and choose the next step.",
            "memories_used": [item["id"] for item in memories],
            "requires_human_decision": True,
        }

    def _llm(self, prompt: str) -> str:
        api_key = os.getenv("AI_API_KEY")
        if not api_key:
            return ""
        body = json.dumps({"model": os.getenv("AI_MODEL", "gpt-4o-mini"), "temperature": 0.1, "messages": [
            {"role": "system", "content": "Advise only. Never claim authority, execute actions, or make decisions for a human."},
            {"role": "user", "content": prompt},
        ]}).encode()
        request = urllib.request.Request(
            f"{os.getenv('AI_BASE_URL', 'https://api.openai.com/v1').rstrip('/')}/chat/completions",
            data=body,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=45) as response:
            return str(json.loads(response.read()) ["choices"][0]["message"]["content"])