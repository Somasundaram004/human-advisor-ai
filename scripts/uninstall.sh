#!/usr/bin/env bash
set -Eeuo pipefail
launchctl bootout "gui/$(id -u)/com.humanadvisor.ai" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/com.humanadvisor.ai.plist"
rm -f "$HOME/.config/autostart/human-advisor-ai.desktop"
systemctl --user disable --now human-advisor-ai.service 2>/dev/null || true
rm -f "$HOME/.config/systemd/user/human-advisor-ai.service"
printf 'Human Advisor AI auto-start removed. Data and virtual environment were left intact.\n'