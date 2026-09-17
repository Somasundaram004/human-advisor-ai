import json
import sqlite3
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    kind TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details TEXT NOT NULL,
                    sensitivity TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    action TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    reason TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    comment TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    decided_at TEXT
                );
            """)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def remember(self, item: dict[str, Any]) -> dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO memories(kind, summary, details, sensitivity) VALUES (?, ?, ?, ?)",
                (item["kind"], item["summary"], json.dumps(item.get("details", {})), item.get("sensitivity", "normal")),
            )
            return {"id": cursor.lastrowid, **item}

    def recall(self, query: str = "", limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as connection:
            if query:
                rows = connection.execute(
                    "SELECT * FROM memories WHERE summary LIKE ? ORDER BY id DESC LIMIT ?",
                    (f"%{query}%", limit),
                ).fetchall()
            else:
                rows = connection.execute("SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [self._memory(row) for row in rows]

    def request_approval(self, action: str, payload: dict[str, Any], reason: str) -> dict[str, Any]:
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO approvals(action, payload, reason) VALUES (?, ?, ?)",
                (action, json.dumps(payload), reason),
            )
            return {"id": cursor.lastrowid, "action": action, "payload": payload, "reason": reason, "status": "pending"}

    def decide(self, approval_id: int, approved: bool, comment: str) -> dict[str, Any] | None:
        status = "approved" if approved else "rejected"
        with self._connect() as connection:
            connection.execute(
                "UPDATE approvals SET status = ?, comment = ?, decided_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'pending'",
                (status, comment, approval_id),
            )
            row = connection.execute("SELECT * FROM approvals WHERE id = ?", (approval_id,)).fetchone()
        return self._approval(row) if row else None

    def pending(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM approvals WHERE status = 'pending' ORDER BY id").fetchall()
        return [self._approval(row) for row in rows]

    @staticmethod
    def _memory(row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        value["details"] = json.loads(value["details"])
        return value

    @staticmethod
    def _approval(row: sqlite3.Row) -> dict[str, Any]:
        value = dict(row)
        value["payload"] = json.loads(value["payload"])
        return value