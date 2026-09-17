from pathlib import Path

from .policy import HumanApprovalPolicy


class CodeWriter:
    def __init__(self, policy: HumanApprovalPolicy):
        self.policy = policy

    def draft(self, filename: str, content: str, reason: str) -> dict:
        safe_name = Path(filename).name
        proposal = {"filename": safe_name, "content": content}
        approval = self.policy.ask("write_code", proposal, reason)
        return {"proposal": proposal, "approval": approval, "written": False, "requires_human_decision": True}