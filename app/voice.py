from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ListeningSession:
    active: bool = False
    consented: bool = False
    started_at: str | None = None


class VoiceModule:
    """Consent-controlled voice boundary; no microphone starts automatically."""

    def __init__(self):
        self.session = ListeningSession()

    def start(self, consent: bool) -> dict:
        if not consent:
            return {"active": False, "requires_explicit_consent": True}
        self.session = ListeningSession(
            active=True,
            consented=True,
            started_at=datetime.now(timezone.utc).isoformat(),
        )
        return self.status()

    def stop(self) -> dict:
        self.session = ListeningSession()
        return self.status()

    def status(self) -> dict:
        return {
            "active": self.session.active,
            "consented": self.session.consented,
            "started_at": self.session.started_at,
            "always_on": False,
            "human_control_required": True,
        }

    def transcribe(self, text: str, speaker: str) -> dict:
        return {"text": text, "speaker": speaker, "provider": "local-text-fallback", "requires_human_confirmation": True}

    def speak(self, text: str) -> dict:
        return {"text": text, "provider": "local-text-fallback", "audio_generated": False}