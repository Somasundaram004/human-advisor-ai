# Human Advisor AI

A human-in-the-loop AI service for remembering incidents, experiences, feelings as user-provided affective context, advice, code drafting, API communication proposals, voice adapters, and explicit feedback learning.

The service is intentionally not an autonomous agent. It does not claim to have feelings, make decisions for a person, run code, write files, or send API requests without human approval. Every consequential request is stored as `pending` and requires the configured approval token. Even after approval, the base service keeps execution disabled; integrate a separately reviewed executor only after adding a second security boundary.

## Modules

- `MemoryStore`: SQLite memory for incidents, facts, user-provided feelings, and feedback.
- `Adviser`: optional OpenAI-compatible advice provider with an offline fallback.
- `HumanApprovalPolicy`: approval queue for API requests, code writes, commands, and other actions.
- `CodeWriter`: creates a code proposal only; it never writes or executes it.
- `APIClient`: creates an API request proposal only; it never sends it.
- `VoiceModule`: consent-controlled listening session with explicit start/stop/status; connect a reviewed speech-to-text/text-to-speech provider later.
- Wake word: `Brosir` activates command handling only inside a consented listening session.
- `LearningModule`: summarizes explicit human feedback into reviewable preferences; it cannot change policy automatically.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
uvicorn app.main:app --reload
```

Windows PowerShell activation:

```powershell
\.venv\Scripts\Activate.ps1
```

Open `http://localhost:8000/docs` for the API documentation. Set a strong `HUMAN_APPROVAL_TOKEN`; do not use the example value in a shared environment.

## Install once and start automatically

The installers register the service to start at user login and restart if the API process exits. The API listens only on `127.0.0.1` by default:

Windows PowerShell:

```powershell
.\scripts\install.ps1
```

macOS or Linux:

```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

The service is then always ready at `http://127.0.0.1:8000/`. Installers open one visible Brosir AI browser window at login. On Windows, the installer uses a scheduled task when policy allows it and falls back to the current-user Startup folder when task registration is denied. The window is not repeatedly forced to the foreground, and closing it does not stop the background API. This does not silently activate the microphone. A user must grant OS microphone permission and explicitly call `/v1/voice/start`; stop listening with `/v1/voice/stop`. The Brosir wake word is processed only during that consented session.

The installers use `requirements.txt` instead of editable package installation so they also work from Windows paths containing `$` characters.

## Voice safety

The service cannot and will not secretly keep your microphone on. A browser or desktop client must request OS microphone permission, show a visible listening indicator, and call the explicit start endpoint:

```bash
curl -X POST http://localhost:8000/v1/voice/start -H 'Content-Type: application/json' -d '{"consent":true}'
curl http://localhost:8000/v1/voice/status
curl -X POST http://localhost:8000/v1/voice/stop
```

Use push-to-talk or a user-enabled wake word in the client. Audio transcription and external voice providers require a separate adapter with consent, retention, and deletion controls. See [docs/architecture.md](docs/architecture.md) for the voice, memory, adviser, proposal, and human approval flow.

## Brosir wake word

After the user grants microphone permission and starts a session, send locally transcribed phrases to the command endpoint. The default wake word is case-insensitive `Brosir` and can be changed with `WAKE_WORD`:

```bash
curl -X POST http://localhost:8000/v1/voice/start -H 'Content-Type: application/json' -d '{"consent":true}'
curl -X POST http://localhost:8000/v1/voice/command -H 'Content-Type: application/json' -d '{"text":"Brosir, remember that the deployment failed","speaker":"human"}'
```

The first phrase beginning with `Brosir` activates a continuous conversation session. Later phrases in the same consented session do not need the wake word again. The session ends when the user chooses Stop, the client disconnects, or the service restarts. The client must send each locally transcribed phrase to `/v1/voice/command`; this backend does not secretly capture audio.

Ordinary conversation, memory capture, advice, and status responses can continue without an approval prompt. Critical actions still require approval: writing or executing code, shell/cluster commands, API calls, external messages, infrastructure changes, credential or permission changes, financial actions, or anything with irreversible side effects. The AI may propose those actions, but it cannot perform them independently.

## Run with Docker

```bash
cp .env.example .env
docker compose up --build
```

The SQLite volume keeps memory across restarts. Use managed encrypted storage and backups for production; SQLite is only a starter implementation.

## Examples

Remember an incident:

```bash
curl -X POST http://localhost:8000/v1/memories -H 'Content-Type: application/json' -d '{"kind":"incident","summary":"Deployment failed after an expired certificate"}'
```

Ask for advice:

```bash
curl -X POST http://localhost:8000/v1/advice -H 'Content-Type: application/json' -d '{"question":"How should I investigate the certificate incident?"}'
```

Request an API action. This returns a pending approval and sends nothing:

```bash
curl -X POST http://localhost:8000/v1/api/request -H 'Content-Type: application/json' -d '{"action":"send_api_request","reason":"Create a support ticket","payload":{"method":"POST","url":"https://example.invalid/tickets","body":{}}}'
```

## Production requirements

- Put the API behind TLS, authentication, rate limiting, and an audit gateway.
- Store sensitive memories encrypted with strict retention and deletion controls.
- Treat feelings as user-provided context, not clinical truth or inferred identity.
- Require two-person approval for high-impact actions.
- Keep code execution, shell access, credentials, and outbound networking outside this base service.
- Add provider-specific voice adapters with explicit consent before recording or transmitting audio.
- Run tests and dependency/security scans in CI before deployment.