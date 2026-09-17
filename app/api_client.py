import json
import urllib.request

from .policy import HumanApprovalPolicy


class APIClient:
    def __init__(self, policy: HumanApprovalPolicy):
        self.policy = policy

    def request(self, method: str, url: str, body: dict, reason: str) -> dict:
        proposal = {"method": method.upper(), "url": url, "body": body}
        approval = self.policy.ask("send_api_request", proposal, reason)
        return {"proposal": proposal, "approval": approval, "sent": False, "requires_human_decision": True}

    @staticmethod
    def approved_request(method: str, url: str, body: dict) -> dict:
        request = urllib.request.Request(url, data=json.dumps(body).encode(), method=method.upper(), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return {"status": response.status, "body": response.read().decode("utf-8", errors="replace")}