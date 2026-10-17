from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


class EventStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.path, timeout=30)
        connection.row_factory = sqlite3.Row
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _init_schema(self) -> None:
        with self.connect() as db:
            db.executescript(
                """
                PRAGMA journal_mode=WAL;
                CREATE TABLE IF NOT EXISTS submissions (
                    response_token TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    master_record_id TEXT,
                    status TEXT NOT NULL DEFAULT 'received',
                    last_error TEXT,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS route_results (
                    response_token TEXT NOT NULL,
                    route TEXT NOT NULL,
                    record_id TEXT,
                    message_id TEXT,
                    status TEXT NOT NULL DEFAULT 'pending',
                    last_error TEXT,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (response_token, route),
                    FOREIGN KEY (response_token) REFERENCES submissions(response_token)
                );
                """
            )

    def receive(self, token: str, payload: dict[str, Any], routes: list[str]) -> None:
        with self.connect() as db:
            db.execute(
                "INSERT OR IGNORE INTO submissions(response_token, payload_json) VALUES(?, ?)",
                (token, json.dumps(payload, ensure_ascii=False, separators=(",", ":"))),
            )
            for route in routes:
                db.execute(
                    "INSERT OR IGNORE INTO route_results(response_token, route) VALUES(?, ?)",
                    (token, route),
                )

    def submission(self, token: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM submissions WHERE response_token=?", (token,)).fetchone()
            return dict(row) if row else None

    def route(self, token: str, route: str) -> dict[str, Any] | None:
        with self.connect() as db:
            row = db.execute("SELECT * FROM route_results WHERE response_token=? AND route=?", (token, route)).fetchone()
            return dict(row) if row else None

    def set_master(self, token: str, record_id: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE submissions SET master_record_id=?, status='routing', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=?", (record_id, token))

    def set_route_record(self, token: str, route: str, record_id: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE route_results SET record_id=?, status='written', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=? AND route=?", (record_id, token, route))

    def set_route_notified(self, token: str, route: str, message_id: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE route_results SET message_id=?, status='notified', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=? AND route=?", (message_id, token, route))

    def set_route_message(self, token: str, route: str, message_id: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE route_results SET message_id=?, status='message_sent', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=? AND route=?", (message_id, token, route))

    def set_route_error(self, token: str, route: str, error: str) -> None:
        with self.connect() as db:
            db.execute("UPDATE route_results SET status='failed', last_error=?, updated_at=CURRENT_TIMESTAMP WHERE response_token=? AND route=?", (error[:2000], token, route))
            db.execute("UPDATE submissions SET status='failed', last_error=?, updated_at=CURRENT_TIMESTAMP WHERE response_token=?", (error[:2000], token))

    def mark_complete_if_ready(self, token: str) -> bool:
        with self.connect() as db:
            remaining = db.execute("SELECT COUNT(*) FROM route_results WHERE response_token=? AND status!='notified'", (token,)).fetchone()[0]
            if remaining == 0:
                db.execute("UPDATE submissions SET status='complete', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=?", (token,))
                return True
            return False

    def mark_written_if_ready(self, token: str) -> bool:
        with self.connect() as db:
            remaining = db.execute(
                "SELECT COUNT(*) FROM route_results WHERE response_token=? AND status NOT IN ('written', 'message_sent', 'notified')",
                (token,),
            ).fetchone()[0]
            if remaining == 0:
                db.execute(
                    "UPDATE submissions SET status='written', last_error=NULL, updated_at=CURRENT_TIMESTAMP WHERE response_token=?",
                    (token,),
                )
                return True
            return False
