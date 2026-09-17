from .store import MemoryStore


class LearningModule:
    """Learns only reviewable preferences from explicit human feedback."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def record_feedback(self, summary: str, details: dict) -> dict:
        return self.store.remember({"kind": "feedback", "summary": summary, "details": details, "sensitivity": "normal"})

    def profile(self) -> dict:
        feedback = self.store.recall("", 100)
        feedback = [item for item in feedback if item["kind"] == "feedback"]
        return {
            "feedback_count": len(feedback),
            "reviewable_preferences": [item["summary"] for item in feedback[-20:]],
            "automatic_policy_changes": False,
            "human_review_required": True,
        }