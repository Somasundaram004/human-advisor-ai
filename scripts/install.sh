#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
command -v python3 >/dev/null 2>&1 || { printf 'Python 3.11+ is required.\n' >&2; exit 1; }
VENV="$ROOT_DIR/.venv"
[[ -d "$VENV" ]] || python3 -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -e "$ROOT_DIR"
[[ -f "$ROOT_DIR/.env" ]] || cp "$ROOT_DIR/.env.example" "$ROOT_DIR/.env"

OS_NAME="$(uname -s)"
if [[ "$OS_NAME" == Darwin ]]; then
  LAUNCH_DIR="$HOME/Library/LaunchAgents"
  mkdir -p "$LAUNCH_DIR"
  cat >"$LAUNCH_DIR/com.humanadvisor.ai.plist" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>com.humanadvisor.ai</string>
<key>ProgramArguments</key><array><string>$VENV/bin/uvicorn</string><string>app.main:app</string><string>--host</string><string>127.0.0.1</string><string>--port</string><string>8000</string></array>
<key>WorkingDirectory</key><string>$ROOT_DIR</string>
<key>RunAtLoad</key><true/>
<key>KeepAlive</key><true/>
</dict></plist>
EOF
  launchctl bootout "gui/$(id -u)/com.humanadvisor.ai" 2>/dev/null || true
  launchctl bootstrap "gui/$(id -u)" "$LAUNCH_DIR/com.humanadvisor.ai.plist"
elif [[ "$OS_NAME" == Linux ]] && command -v systemctl >/dev/null 2>&1; then
  SERVICE_DIR="$HOME/.config/systemd/user"
  mkdir -p "$SERVICE_DIR"
  cat >"$SERVICE_DIR/human-advisor-ai.service" <<EOF
[Unit]
Description=Human Advisor AI
After=network-online.target

[Service]
WorkingDirectory=$ROOT_DIR
ExecStart=$VENV/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=default.target
EOF
  systemctl --user daemon-reload
  systemctl --user enable --now human-advisor-ai.service
else
  printf 'Installed dependencies. Start manually with: %s\n' "$VENV/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000"
fi
printf 'Human Advisor AI is installed at http://127.0.0.1:8000/docs\n'
printf 'Microphone access remains opt-in and must be started by the user.\n'