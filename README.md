# Human Advisor AI

A human-in-the-loop AI service for remembering incidents, experiences, feelings as user-provided affective context, advice, code drafting, API communication proposals, voice adapters, and explicit feedback learning.

The service is intentionally not an autonomous agent. It does not claim to have feelings, make decisions for a person, run code, write files, or send API requests without human approval. Every consequential request is stored as `pending` and requires the configured approval token. Even after approval, the base service keeps execution disabled; integrate a separately reviewed executor only after adding a second security boundary.

## Modules

- `MemoryStore`: SQLite memory for incidents, facts, user-provided feelings, and feedback.
- `Adviser`: optional OpenAI-compatible advice provider with an offline fallback.
- `HumanApprovalPolicy`: approval queue for API requests, code writes, commands, and other actions.
- `CodeWriter`: creates a code proposal only; it never writes or executes it.
- `APIClient`: creates an API request proposal only; it never sends it.
- `VoiceModule`: provider-neutral text fallback; connect a reviewed speech-to-text/text-to-speech provider later.
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