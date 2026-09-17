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
        source = "llm" if answer else "local"
        return {
            "answer": answer or self._local_answer(question, memories),
            "answer_source": source,
            "memories_used": [item["id"] for item in memories],
            "requires_human_decision": False,
        }

    @staticmethod
    def _local_answer(question: str, memories: list[dict]) -> str:
        lowered = question.casefold()
        remembered = "; ".join(item["summary"] for item in memories[:3])
        if any(word in lowered for word in ("incident", "failed", "error", "outage", "broken")):
            return "Start with the timeline, exact error, recent changes, affected scope, and last known good state. Preserve logs before changing production. Related memory: " + (remembered or "none recorded")
        if any(word in lowered for word in ("deploy", "release", "upgrade")):
            return "Use a reviewed plan, a dry run, health checks, a rollback plan, and a staged rollout. I will not deploy or upgrade anything without the required human approval."
        if any(word in lowered for word in ("remember", "recall", "what do you know")):
            return "Here is the closest stored context: " + (remembered or "I do not have a matching memory yet.")
        if any(word in lowered for word in ("feel", "feeling", "angry", "sad", "worried", "happy")):
            return "I can record the feeling you describe as user-provided context, but I do not experience feelings or infer a diagnosis."
        if any(word in lowered for word in ("hello", "hi", "brosir")):
            return "I am here and ready to help. Ask a question, describe an incident, or tell me what context you want remembered."
        return "I can answer this locally using stored context and safety rules. Give me the goal, relevant facts, constraints, and desired outcome."

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