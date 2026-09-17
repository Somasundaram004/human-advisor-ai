from dataclasses import dataclass
from datetime import datetime, timezone
import os


@dataclass
class ListeningSession:
    active: bool = False
    consented: bool = False
    started_at: str | None = None
    activated: bool = False
    last_command: str | None = None


class VoiceModule:
    """Consent-controlled voice boundary; no microphone starts automatically."""

    def __init__(self):
        self.session = ListeningSession()
        self.wake_word = os.getenv("WAKE_WORD", "Brosir")

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

    def process_phrase(self, text: str, speaker: str) -> dict:
        normalized = text.strip()
        wake_detected = normalized.casefold().startswith(self.wake_word.casefold())
        if not self.session.active or not self.session.consented:
            return {
                "accepted": False,
                "reason": "voice session is not active with consent",
                "wake_word": self.wake_word,
                "requires_explicit_consent": True,
            }
        if not wake_detected and not self.session.activated:
            return {"accepted": False, "reason": "wake word not detected", "wake_word": self.wake_word}
        command = normalized[len(self.wake_word):].lstrip(" ,:;.!?") if wake_detected else normalized
        self.session.activated = True
        self.session.last_command = command
        return {
            "accepted": True,
            "activated": True,
            "wake_word_detected": wake_detected,
            "continuous_session": True,
            "wake_word": self.wake_word,
            "command": command,
            "speaker": speaker,
            "next_step": "route ordinary conversation directly; create a pending approval for critical actions",
            "human_approval_required": False,
        }

    def status(self) -> dict:
        return {
            "active": self.session.active,
            "consented": self.session.consented,
            "started_at": self.session.started_at,
            "always_on": False,
            "human_control_required": True,
            "wake_word": self.wake_word,
            "activated": self.session.activated,
            "last_command": self.session.last_command,
        }

    def transcribe(self, text: str, speaker: str) -> dict:
        return {"text": text, "speaker": speaker, "provider": "local-text-fallback", "requires_human_confirmation": True}

    def speak(self, text: str) -> dict:
        return {"text": text, "provider": "local-text-fallback", "audio_generated": False}