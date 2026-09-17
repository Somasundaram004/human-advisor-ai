from .store import MemoryStore


class HumanApprovalPolicy:
    """Every consequential action is paused until a human decides."""

    def __init__(self, store: MemoryStore):
        self.store = store

    def ask(self, action: str, payload: dict, reason: str) -> dict:
        return self.store.request_approval(action, payload, reason)

    def can_execute(self, approval_id: int) -> bool:
        return any(item["id"] == approval_id and item["status"] == "approved" for item in self.store.pending())

    def execute(self, approval_id: int) -> dict:
        raise PermissionError("Execution is intentionally disabled in the base service. Integrate a reviewed executor behind a second approval boundary.")