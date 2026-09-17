class VoiceModule:
    """Provider-neutral voice boundary; no audio is sent anywhere by default."""

    def transcribe(self, text: str, speaker: str) -> dict:
        return {"text": text, "speaker": speaker, "provider": "local-text-fallback", "requires_human_confirmation": True}

    def speak(self, text: str) -> dict:
        return {"text": text, "provider": "local-text-fallback", "audio_generated": False}