import os

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import FileResponse

from .adviser import Adviser
from .api_client import APIClient
from .code_writer import CodeWriter
from .models import ActionRequest, AdviceInput, ApprovalInput, MemoryInput, VoiceInput
from .learning import LearningModule
from .policy import HumanApprovalPolicy
from .store import MemoryStore
from .voice import VoiceModule

store = MemoryStore(os.getenv("DATABASE_PATH", "data/memory.db"))
policy = HumanApprovalPolicy(store)
adviser = Adviser(store)
voice = VoiceModule()
api_client = APIClient(policy)
code_writer = CodeWriter(policy)
learning = LearningModule(store)
app = FastAPI(title="Human Advisor AI", version="0.1.0")
UI_PATH = os.path.join(os.path.dirname(__file__), "static", "index.html")
CRITICAL_TERMS = (
    "send", "delete", "deploy", "execute", "run command", "write code", "change permission",
    "change credential", "transfer money", "publish", "email", "message", "production",
)


def is_critical(command: str) -> bool:
    lowered = command.casefold()
    return any(term in lowered for term in CRITICAL_TERMS)


@app.get("/")
def ui() -> FileResponse:
    return FileResponse(UI_PATH)


def require_human_token(token: str | None) -> None:
    expected = os.getenv("HUMAN_APPROVAL_TOKEN")
    if not expected or token != expected:
        raise HTTPException(status_code=401, detail="Human approval token is required")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "human_approval_required": True}


@app.post("/v1/memories")
def remember(item: MemoryInput) -> dict:
    return store.remember(item.model_dump())


@app.get("/v1/memories")
def recall(query: str = "", limit: int = 20) -> list[dict]:
    return store.recall(query, min(limit, 100))


@app.post("/v1/advice")
def advise(item: AdviceInput) -> dict:
    return adviser.answer(item.question, item.context)


@app.post("/v1/learning/feedback")
def learn(item: MemoryInput) -> dict:
    if item.kind != "feedback":
        raise HTTPException(status_code=400, detail="kind must be feedback")
    return learning.record_feedback(item.summary, item.details)


@app.get("/v1/learning/profile")
def learning_profile() -> dict:
    return learning.profile()


@app.post("/v1/actions")
def request_action(item: ActionRequest) -> dict:
    return policy.ask(item.action, item.payload, item.reason)


@app.get("/v1/approvals")
def approvals(x_human_approval_token: str | None = Header(default=None)) -> list[dict]:
    require_human_token(x_human_approval_token)
    return store.pending()


@app.post("/v1/approvals/{approval_id}")
def decide(approval_id: int, decision: ApprovalInput, x_human_approval_token: str | None = Header(default=None)) -> dict:
    require_human_token(x_human_approval_token)
    result = store.decide(approval_id, decision.approved, decision.comment)
    if result is None:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return result


@app.post("/v1/code/draft")
def draft_code(item: ActionRequest) -> dict:
    if item.action != "write_code":
        raise HTTPException(status_code=400, detail="action must be write_code")
    return code_writer.draft(item.payload.get("filename", "proposal.txt"), item.payload.get("content", ""), item.reason)


@app.post("/v1/api/request")
def api_request(item: ActionRequest) -> dict:
    if item.action != "send_api_request":
        raise HTTPException(status_code=400, detail="action must be send_api_request")
    return api_client.request(item.payload.get("method", "POST"), item.payload.get("url", ""), item.payload.get("body", {}), item.reason)


@app.post("/v1/voice/transcribe")
def transcribe(item: VoiceInput) -> dict:
    return voice.transcribe(item.text, item.speaker)


@app.post("/v1/voice/command")
def voice_command(item: VoiceInput) -> dict:
    result = voice.process_phrase(item.text, item.speaker)
    if not result.get("accepted"):
        return result
    command = result["command"]
    if is_critical(command):
        result.update({
            "critical_action": True,
            "human_approval_required": True,
            "answer": "This request may create an external or irreversible side effect. I will prepare a proposal, but I need your approval before any action.",
        })
        return result
    result["critical_action"] = False
    result["answer"] = adviser.answer(command, {"source": "continuous_brosir_voice", "speaker": item.speaker})
    result["human_approval_required"] = False
    return result


@app.post("/v1/voice/start")
def start_voice(item: dict) -> dict:
    return voice.start(bool(item.get("consent", False)))


@app.post("/v1/voice/stop")
def stop_voice() -> dict:
    return voice.stop()


@app.get("/v1/voice/status")
def voice_status() -> dict:
    return voice.status()


@app.post("/v1/voice/speak")
def speak(item: AdviceInput) -> dict:
    return voice.speak(item.question)